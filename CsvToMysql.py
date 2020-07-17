import csv

f = open(r'\\DANGAM_NEW\working\01c.사업_교감\2019.구르미랑\01. 자료_분석_시장조사\02. 정보큐레이션\데이터맵\메타데이터_원장\이준재\A0111_반려동물_등록기관_20200424.csv', 'r', encoding='utf-8')
rdr = csv.reader(f)
for line in rdr:
    print(line)

with open("out.csv", "w", newline='', encoding='utf-8-sig') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)
