import datetime
import pymysql
import re


class CrawlClass(object):
    def __init__(self):
        self.host = 'localhost'

    def insert(self):
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
             WHERE CONVENTION_NAME = 'atcenter'
        """
        curs.execute(sql)
        rows = curs.fetchall()
        cnt = 0
        for row in rows:
            cnt += 1
            title_atpattern = r"<th\b[^>]*>(.*?)<\/th>"
            title_pattern = r"(캣|도그|펫|동물|애견|애완|교육|자격증|훈련)"  # row[3] => 페이지소스
            match = re.findall(title_atpattern, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            at_host = r'<li><span class="tit">주최<\/span>(.*?)<\/li>'
            at_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            at_date = r'<li><span class="tit">기간<\/span>(.+)<\/li>'
            at_place = r'<li><span class="tit">장소<\/span>(.*?)<\/li>'
            at_time = r'시간\<\/span\>[\n\t ]*(.*)[\n\t ]*\<\/li\>'
            at_money = r'<li><span class="tit">입장료<\/span>(.*?)<\/li>'
            at_phone = r'<li><span class="tit">행사문의<\/span>(.*?)<\/li>'
            at_url = row[4]  # 해당 페이지 주소
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            pattern_home = r'홈페이지\<\/span\>\n\<a href\=\".*\"\>(.*)\<\/a\>'
            z_start = ''
            z_end = ''
            if match2:
                print(match[0])  # title
                host = re.findall(at_host, row[3])
                manage = re.findall(at_manage, row[3])
                date = re.findall(at_date, row[3])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                at_index = tempdate.find('-')
                at_start = tempdate[0:at_index].replace('.', '-')
                at_end = tempdate[at_index+2:len(tempdate)].replace('.', '-')
                place = re.findall(at_place, row[3])
                time = re.findall(at_time, row[3])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                at_t_index = temptime.find('-')
                at_t_start = temptime[0:at_t_index]
                at_t_end = temptime[at_t_index+2:len(temptime)]
                money = re.findall(at_money, row[3])
                phone = re.findall(at_phone, row[3])
                home = re.findall(pattern_home, row[3])
                if len(home) > 0:
                    str_home = home[0]
                else:
                    str_home = ''
                try:
                    print("주최 {}".format(host[0]))
                    print("주관 {}".format(manage[0]))
                    print("시작 {}".format(at_start))
                    print("종료 {}".format(at_end))
                    print("장소 {}".format(place[0]))
                    print("시간 {}".format(at_t_start))
                    print("시간 {}".format(at_t_end))
                    print("돈 {}".format(money[0]))
                    print("번호 {}".format(phone[0]))
                    print("홈페이지 {}".format(str_home))
                    z_start = datetime.datetime.strptime(at_start.strip(), '%Y-%m-%d')
                    z_end = datetime.datetime.strptime(at_end.strip(), '%Y-%m-%d')
                except ValueError:
                    if at_end == '2004--':
                        z_end = datetime.datetime.strptime("2004-03-07", '%Y-%m-%d')
                query = """insert into refine_schedule
                        (convention_name, event_name, full_address, 
                        place_dept1, place_dept2, place_dept3, date_start, date_end,
                        time_start, time_end, phone_number, home_page, manage, host,
                        money, event_desc, source_url, source_name, reg_date) 
                        values(%s, %s, %s, %s, %s, %s, %s, %s
                        , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                curs.execute(query,
                             ('atcenter', match[0],
                              'atcenter 서울특별시 서초구 강남대로 27 {}'.format(place[0]),
                              '서울특별시', '서초구', '강남대로 27',
                              z_start, z_end, at_t_start, at_t_end,
                              phone[0], str_home, manage[0], host[0], money[0], '',
                              at_url, 'atcenter', reg_date))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.insert()