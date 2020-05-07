import pymysql


class CrawlClass(object):
    def __init__(self):
        self.conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )

    def return_conn(self):
        return self.conn

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def content_select(self, data):
        curs = self.conn.cursor()
        sql = """ SELECT *
                    FROM event_original
                   WHERE convention_name = '{}'
        """.format(data)
        curs.execute(sql)
        rows = curs.fetchall()
        return rows

    def content_insert(self, data):
        curs = self.conn.cursor()
        query = """insert into event_refine
            (convention_name, event_name, event_type, place,  
            date_start, date_end, time_start, time_end, 
            phone, home_page, manage, host, 
            money, source_url, reg_date) 
            values
            (%s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s)
        """
        curs.execute(query,
                     (data['convention_name'], data['event_name'], data['event_type'], data['place'],
                      data['date_start'], data['data_end'], data['time_start'], data['time_end'],
                      data['phone'], data['home_page'], data['manage'], data['host'],
                      data['money'], data['source_url'], data['reg_date']
                      )
                     )
        self.conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
