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

    def content_insert(self, data, flag):
        curs = self.conn.cursor()
        query_event = """insert into event_original
        (convention_name, event_name, event_type, event_start_date, page_source, source_url, home_page, reg_date) 
        values(%s, %s, %s, %s, %s, %s, %s, %s)
        """
        query_raw = """insert into event_refine
        
        """
        if flag == 'original':
            curs.execute(query_event,
                         (data.get('convention_name'),
                          data.get('event_name'),
                          data.get('event_type'),
                          data.get('event_start_date'),
                          data.get('page_source'),
                          data.get('source_url'),
                          data.get('home_page'),
                          data.get('reg_date')
                          ))
        else:
            curs.execute(query_raw,
                         (data['convention_name'],
                          data['page_source'],
                          data['contents'],
                          data['source_url'],
                          data['home_page'],
                          data['reg_date'],
                          data['event_id']
                          ))
        self.conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
