import pymysql
import os

output = "id_replace_v_comp_id"

dbs = [
    "matcheasy_new",
    "staffcloud_crm",
    "staffcloud_oa",
    "staffcloud_perf",
    "staffcloud_salary",
    "staffcloud_staff",
    "staffcloud_study",
    "user_business",
    "user_info",
    "user_system",
]

# 配置数据库连接
db_config = {
    'host': 'rm-0jlty78wspyjbg764co.rwlb.rds.aliyuncs.com',
    'port': 3306,
    'user': 'root_user',
    'password': 'Staffcloud&2024',
    'charset': 'utf8mb3',
    'autocommit': True
}


def get_base_tables(cursor):
    """
    只获取物理表（不包含视图）
    """
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
    # 结果行：[('table_name', 'BASE TABLE')]，取第一个元素为表名
    return [
        row[0]
        for row in cursor.fetchall()
        if row[0] != "z_id_mapping" and not row[0].startswith("t_")
    ]


def get_bigint_columns(cursor, table):
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    return [
        row[0]
        for row in cursor.fetchall()
        if row[1].startswith("bigint") and row[0] != "district_id"
    ]


def get_id_mapping(cursor):
    cursor.execute(
        "SELECT distinct source_comp_id as source_id, real_comp_id as target_id FROM sys_trigger.v_comp_id_mapping WHERE create_time > '2026-01-06 20:22:00' and real_comp_id IS NOT NULL and source_comp_id is not NULL and real_comp_id != source_comp_id;")
    return cursor.fetchall()


def need_update_cols(cursor, table, cols, source_ids):
    if not cols or not source_ids:
        return []

    # 去重（可选）
    source_ids = list(dict.fromkeys(source_ids))

    placeholders = ",".join(["%s"] * len(source_ids))

    select_parts = ", ".join([
        f"EXISTS(SELECT 1 FROM `{table}` WHERE `{c}` IN ({placeholders}) LIMIT 1) AS `{c}`"
        for c in cols
    ])
    sql = f"SELECT {select_parts}"

    # 每个 EXISTS 都需要一份 source_ids 参数
    params = []
    for _ in cols:
        params.extend(source_ids)

    cursor.execute(sql, params)
    row = cursor.fetchone()

    return [c for c, flag in zip(cols, row) if flag]


def export(database):
    db_config['database'] = database
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 1. 获取所有物理表和bigint字段
    tables = get_base_tables(cursor)
    table_bigint_cols = {}
    for table in tables:
        cols = get_bigint_columns(cursor, table)
        if cols:
            table_bigint_cols[table] = cols

    # 2. 获取ID映射
    id_mapping = get_id_mapping(cursor)
    source_ids = [s for s, _ in id_mapping]

    # 3. 生成SQL
    update_sqls = []
    rollback_sqls = []
    items = table_bigint_cols.items()
    index = 1
    for table, cols in items:
        print(f"\r> 正在生成SQL -- {database} -- [{index}/{len(items)}] {table}", end="", flush=True)
        for col in need_update_cols(cursor, table, cols, source_ids):
            for source_id, target_id in id_mapping:
                # 正向替换
                update_sqls.append(
                    f"UPDATE IGNORE `{database}`.`{table}` SET `{col}`={target_id} WHERE `{col}`={source_id};"
                )
                # 逆向回滚
                rollback_sqls.append(
                    f"UPDATE IGNORE `{database}`.`{table}` SET `{col}`={source_id} WHERE `{col}`={target_id};"
                )
        index = index + 1
    # 4. 写入文件
    with open(f"{output}/{database}/update.sql", "w", encoding="utf-8") as f:
        f.write('\n'.join(update_sqls))

    with open(f"{output}/{database}/rollback.sql", "w", encoding="utf-8") as f:
        f.write('\n'.join(rollback_sqls))

    print("\n√ SQL文件已生成 -- " + database + "\n")
    cursor.close()
    conn.close()


if __name__ == '__main__':
    for db in dbs:
        dir_path = os.path.join(output, db)
        os.makedirs(dir_path, exist_ok=True)
        export(db)
