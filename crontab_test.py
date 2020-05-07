import pymysql


def crontab_test():
    conn = pymysql.connect(
        db='yojido', user='yojido', password='dg202004@#',
        host='dev.thegam.io', port=3306, charset='utf8mb4'
    )
    curs = conn.cursor()
    sql = '''select * from event'''
    curs.execute(sql)
    rows = curs.fetchall()
    print(rows)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    crontab_test()
