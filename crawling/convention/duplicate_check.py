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

    def close(self):
        self.conn.close()

    def select(self, convention):
        curs = self.conn.cursor()
        query_raw = """SELECT convention_name, event_name, event_start_date, source_url FROM event_original
        WHERE event_start_date > NOW() AND convention_name = %s
        """
        curs.execute(query_raw,
                     (convention,
                      ))
        self.conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
        return curs.fetchall()

    def duplicate_check(self, crawled, convention_name):
        return_list = []
        selected = self.select(convention=convention_name)
        for cra_row in crawled:
            duplicate_flag = 0
            for sel_row in selected:
                if sel_row[1] == cra_row['event_name']:
                    if sel_row[2] == cra_row['event_start_date']:
                        duplicate_flag += 1
            if duplicate_flag == 0:
                print(cra_row['event_name'])
                return_list.append(cra_row)
        return return_list


if __name__ == '__main__':
    cc = CrawlClass()
    a = cc.select('atcenter')
    for aa in a:
        print(aa)