import re
import csv

input_file = '../res/resume_headhunter_detail.sql'
output_file = '../res/resume_headhunter_detail_id_headhunter_id.csv'

# 正则提取 id、SET 里的 headhunter_id、WHERE 里的 headhunter_id
pattern = re.compile(
    r"SET.*?`id`=(\d+),.*?`headhunter_id`=(\d+),.*?WHERE.*?`headhunter_id`=(\d+)",
    re.DOTALL
)

rows = []

with open(input_file, 'r', encoding='utf-8') as infile:
    for line in infile:
        match = pattern.search(line)
        if match:
            id_, headhunter_id_set, headhunter_id_where = match.groups()
            # 只保留 where 的 headhunter_id 为 94504727，并且两个 headhunter_id 不相等
            if headhunter_id_where == '94504727' and headhunter_id_set != headhunter_id_where:
                rows.append([id_, headhunter_id_set, headhunter_id_where])

with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['id', 'headhunter_id_in_set', 'headhunter_id_in_where'])
    writer.writerows(rows)

print(f'已提取到 {output_file}')