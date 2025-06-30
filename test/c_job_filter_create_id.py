import re

input_file = "c_job_update.sql"
output_file = "c_job_create_id_pairs.csv"

with open(input_file, "r", encoding="utf-8") as fin:
    content = fin.read()

sqls = [s.strip() for s in content.split(";") if "UPDATE" in s and s.strip()]

with open(output_file, "w", encoding="utf-8") as fout:
    # 可选：写表头
    # fout.write("set_create_id,where_create_id,where_job_id\n")
    for sql in sqls:
        set_match = re.search(r"\bSET\b(.*?)\bWHERE\b", sql, flags=re.IGNORECASE | re.DOTALL)
        where_match = re.search(r"\bWHERE\b(.*)", sql, flags=re.IGNORECASE | re.DOTALL)
        if set_match and where_match:
            set_part = set_match.group(1)
            where_part = where_match.group(1)
            set_id_match = re.search(r"`create_id`\s*=\s*(\d+)", set_part)
            where_id_match = re.search(r"`create_id`\s*=\s*(\d+)", where_part)
            job_id_match = re.search(r"`job_id`\s*=\s*(\d+)", where_part)
            if set_id_match and where_id_match and job_id_match:
                set_id = set_id_match.group(1)
                where_id = where_id_match.group(1)
                job_id = job_id_match.group(1)
                if where_id == "94504727" and set_id != "94504727":
                    fout.write(f"{set_id},{where_id},{job_id}\n")