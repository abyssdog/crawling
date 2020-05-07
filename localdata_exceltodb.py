import pymysql
from openpyxl import Workbook
from openpyxl import load_workbook


# 엑셀파일 DB Insert
def insert_excel_to_db():
    conn = pymysql.connect(host='127.0.0.1', user='root', port=3306,
                           password='dangam1234', db='convention', charset='utf8mb4')
    try:
        with conn.cursor() as curs:
            sql = """insert into animal_hospital values(
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            wb = load_workbook(r'C:\동물병원.xlsx', data_only=True)
            ws = wb['동물병원_1']

            iter_rows = iter(ws.rows)
            next(iter_rows)
            # row[0] = 번호, 28개
            for row in iter_rows:
                curs.execute(sql, (
                    row[0].value, row[1].value, row[2].value, row[3].value, row[4].value,
                    row[5].value, row[6].value, row[7].value, row[8].value, row[9].value,
                    row[10].value, row[11].value, row[12].value, row[13].value, row[14].value,
                    row[15].value, row[16].value, row[17].value, row[18].value, row[19].value,
                    row[20].value, row[21].value, row[22].value, row[23].value, row[24].value,
                    row[25].value, row[26].value, row[27].value
                ))
            conn.commit()
    finally:
        conn.close()
        wb.close()


if __name__ == "__main__":
    insert_excel_to_db()
