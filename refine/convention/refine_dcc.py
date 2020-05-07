import datetime
import pymysql
import re


class CrawlClass(object):
    def __init__(self):
        self.host = 'localhost'

    def test_insert1(self):
        conn = pymysql.connect(
            host=self.host,
            port=3306,
            user='root',
            password='dangam1234',
            db='convention',
            charset='utf8'
        )
        curs = conn.cursor()
        sql = """
            SELECT *
              FROM RAW_SCHEDULE
             WHERE CONVENTION_NAME = 'dcc'
        """
        curs.execute(sql)
        rows = curs.fetchall()
        cnt = 0
        for row in rows:
            cnt += 1
            title_dcc = r'txttitle\".*\>(.*)\<\/th\>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            match = re.findall(title_dcc, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            pattern_host = r'\"주최자\".*\n*.*\n*.*\"txtcheck\"\>(.*)\<\/td\>'
            # pattern_manage = r'주관\<\/th\>\n\<td\>[\n\t ]*(.*)[\n\t ]*\<\/td\>'
            pattern_date = r'\"행사기간\".*\n*.*\n*.*\"txtdate\"\>(.*)\<\/td\>'  #
            pattern_time = r'\"행사시간\".*\n*.*\n*.*\"txtdate\"\>(.*)\<\/td\>'  #
            pattern_place = r'\"행사장소\".*\n*.*\n*.*\"txtcheck\"\>(.*)\<\/td\>'  #
            # pattern_money = r'입장료\<\/th\>\n\<td\>(.*)\<\/td\>'
            # pattern_phone = r'문의처\<\/th\>\n\<td\>(.*)\<\/td\>'
            # pattern_url = row[4]  # 해당 페이지 주소
            # pattern_home = r'행사홈페이지\<\/th\>\n.*\<a.*\>(.*)\<\/a\>'
            if match2:
                print(match[0])  # title
                place = re.findall(pattern_place, row[3])
                if len(place) != 0:
                    str_place = place[0]
                else:
                    str_place = ''
                date = re.findall(pattern_date, row[3])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = tempdate[0:date_index].replace('년 ', '-').replace('월 ', '-').replace('일', '')
                date_end = tempdate[date_index+1:len(tempdate)].replace('년 ', '-').replace('월 ', '-').replace('일', '')
                time = re.findall(pattern_time, row[3])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                host = re.findall(pattern_host, row[3])
                if len(host) != 0:
                    str_host = host[0]
                else:
                    str_host = ''
                print("주최 {}".format(str_host))
                print(date)
                print(datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d'))
                d_start = datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d')
                print(datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d'))
                d_end = datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d')
                print("장소 {}".format(str_place))

                query = """insert into refine_schedule
                        (convention_name, event_name, full_address, 
                        place_dept1, place_dept2, place_dept3, date_start, date_end,
                        time_start, time_end, phone_number, home_page, manage, host,
                        money, event_desc, source_url, source_name, reg_date) 
                        values(%s, %s, %s, %s, %s, %s, %s, %s
                        , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                '''executed = curs.execute(query,
                                        ('dcc', match[0],
                                         'dcc 대전 유성구 엑스포로 107 {place}'.format(place=str_place),
                                         '대전시', '유성구', '엑스포로 107',
                                         d_start, d_end, time_start, time_end,
                                         '',
                                         '', '', str_host, '', '',
                                         pattern_url, 'dcc', reg_date))
        conn.commit()'''
        conn.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()