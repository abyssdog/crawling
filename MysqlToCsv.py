import csv
import pymysql

conn = pymysql.connect(
                charset='utf8',
                db='convention',
                host='localhost',
                password='dangam1234',
                port=3306,
                user='root'
            )
cursor = conn.cursor()
cursor.execute(""" SELECT * FROM event_refine order by date_start """)
with open("out.csv", "w", newline='', encoding='utf-8-sig') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([i[0] for i in cursor.description])
    csv_writer.writerows(cursor)
