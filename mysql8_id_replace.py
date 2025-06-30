import pymysql

# 配置数据库连接
db_config = {
    'host': 'localhost',
    'port': 33306,
    'user': 'root_user',
    'password': 'Staffcloud&2024',
    'database': 'matcheasy_new',
    'charset': 'utf8mb3',
    'autocommit': True
}

def get_base_tables(cursor):
    """
    只获取物理表（不包含视图）
    """
    cursor.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';")
    # 结果行：[('table_name', 'BASE TABLE')]，取第一个元素为表名
    return [row[0] for row in cursor.fetchall() if row[0] != "z_id_mapping"]

def get_bigint_columns(cursor, table):
    cursor.execute(f"SHOW COLUMNS FROM `{table}`")
    return [row[0] for row in cursor.fetchall() if row[1].startswith('bigint')]

def get_id_mapping(cursor):
    cursor.execute("SELECT source_id, target_id FROM z_id_mapping WHERE target_id IS NOT NULL")
    return cursor.fetchall()

def main():
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

    # 3. 生成SQL
    update_sqls = []
    rollback_sqls = []
    for table, cols in table_bigint_cols.items():
        for col in cols:
            for source_id, target_id in id_mapping:
                # 正向替换
                update_sqls.append(
                    f"-- {table}.{col}: {source_id} -> {target_id}\n"
                    f"UPDATE `{table}` SET `{col}`={target_id} WHERE `{col}`={source_id};"
                )
                # 逆向回滚
                rollback_sqls.append(
                    f"-- {table}.{col}: {target_id} -> {source_id}\n"
                    f"UPDATE `{table}` SET `{col}`={source_id} WHERE `{col}`={target_id};"
                )

    # 4. 写入文件
    with open("update.sql", "w", encoding="utf-8") as f:
        f.write('\n'.join(update_sqls))

    with open("update_rollback.sql", "w", encoding="utf-8") as f:
        f.write('\n'.join(rollback_sqls))

    print("SQL文件已生成。")
    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()