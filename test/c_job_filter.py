import re
import chardet

job_ids = [
    1261,1262,1263,1264,1310,1311,1369,1397,1398,1399,1763,1777,1211,1315,1459,1725,
    1386,1401,1402,1857,1798,1874,1880,1470,1524,1881,1219,1269,1378,1441,1469,1519,
    1547,1772,1877,1863,1335,1545,1437,1413,1732,1776,1844,1870,1292,1293,1294,1305,
    1309,1374,1375,1321,1322,1364,1444,1200,1203,1204,1209,1862,1873,1530,1516,1206,
    1300,1351,1356,1384,1414,1415,1235,1232,1373,1508,1327,1334,1368,1611,1632,1815,
    1405,1406,1407,1436,1325,1420,1341,1342,1343,1352,1372,1411,1438,1199,1205,1207,
    1214,1217,1218,1234,1237,1242,1243,1268,1283,1289,1290,1318,1365,1376,1377,1385,
    1273,1274,1275,1276,1284,1285,1286,1287,1291,1301,1303,1304,1869,1280,1281,1319,
    1388,1389,1416,1302,1307,1359,1360,1361,1379,1212,1239,1244,1282,1297,1298,1421,
    1854,1717,1730,1830,1442,1201,1216,1258,1278,1279,1295,1296,1308,1316,1324,1329,
    1370,1371,1380,1383,1418,1445,1448,1450,1458,1753,1773,1809,1231,1233,1332,1358,
    1240,1871
]
job_id_set = set(str(jid) for jid in job_ids)

# 检测编码
with open("../rollback-4.sql", "rb") as f:
    data = f.read(4096)
    result = chardet.detect(data)
    encoding = result['encoding']
    print("检测到的编码:", encoding)

# 允许有无反引号、单引号、空格，精准匹配c_job表
update_c_job_pattern = re.compile(
    r"UPDATE\s+[`'\"]?matcheasy_new[`'\"]?\s*\.\s*[`'\"]?c_job[`'\"]?\s", re.IGNORECASE)

# where中的job_id
where_job_id_pattern = re.compile(r"(?:WHERE|AND)\s+`job_id`\s*=\s*(\d+)", re.IGNORECASE)

with open("../rollback-4.sql", "r", encoding=encoding) as fin, \
     open("c_job_update.sql", "w", encoding="utf-8") as fout_matched, \
     open("../update_without_c_job.sql", "w", encoding="utf-8") as fout_other:

    buffer = []
    for line in fin:
        buffer.append(line)
        if line.strip().endswith(";"):
            sql_block = "".join(buffer)
            # 只处理c_job表
            if update_c_job_pattern.search(sql_block):
                # 抓WHERE里的所有job_id=xxx
                matches = where_job_id_pattern.findall(sql_block)
                if any(jid in job_id_set for jid in matches):
                    fout_matched.write(sql_block)
                else:
                    fout_other.write(sql_block)
            else:
                fout_other.write(sql_block)
            buffer = []