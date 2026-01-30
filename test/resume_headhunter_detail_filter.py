import chardet

input_file = '../rollback-4.sql'  # 输入文件名
output_file = '../res/resume_headhunter_detail.sql'  # 输出文件名

prefix = 'UPDATE `matcheasy_new`.`resume_headhunter_detail`'

with open("../rollback-4.sql", "rb") as f:
    data = f.read(4096)
    result = chardet.detect(data)
    encoding = result['encoding']
    print("检测到的编码:", encoding)

with open(input_file, 'r', encoding=encoding) as infile, \
     open(output_file, 'w', encoding='utf-8') as outfile:
    for line in infile:
        if line.startswith(prefix):
            outfile.write(line)
