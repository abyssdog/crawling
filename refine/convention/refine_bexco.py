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
             WHERE CONVENTION_NAME = 'bexco'
        """
        curs.execute(sql)
        rows = curs.fetchall()
        cnt = 0
        for row in rows:
            cnt += 1
            title_bexco = r"<h3\b[^>]*>(.*?)<\/h3>"
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            match = re.findall(title_bexco, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            # 여기 아래다가 엑셀 파일에 저장하는걸 만들면 될듯
            pattern_host = r'\<dt\>주최\/주관\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            # pattern_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            pattern_date = r'\<dt\>기간<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_place = r'\<dt\>장소\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_time = r'\<dt\>시간\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_money = r'\<dt\>관람료\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_phone = r'\<dt\>전화\<\/dt\>\n\<dd\>\n\t{4}(.*?)\n\t{4}\<\/dd\>'
            pattern_url = row[4]  # 해당 페이지 주소
            pattern_home = r'\<dt\>홈페이지\<\/dt\>\n\<dd\>\n\t{4}(.*?)\n\t{4}\<\/dd\>'
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            if match2:
                print(match[0])  # title
                place = re.findall(pattern_place, row[3])
                date = re.findall(pattern_date, row[3])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = tempdate[0:date_index].replace('.', '-')
                date_end = tempdate[date_index+1:len(tempdate)].replace('.', '-')
                time = re.findall(pattern_time, row[3])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                time_index = temptime.find('~')
                time_start = temptime[0:time_index]
                time_end = temptime[time_index+1:len(temptime)]
                phone = re.findall(pattern_phone, row[3])
                str_phone = phone[0].strip()
                if phone[0] == '-- ' or phone[0] == ' ':
                    str_phone = ''
                home = re.findall(pattern_home, row[3])
                if len(home) > 0:
                    str_home = home[0].strip()
                else:
                    str_home = ''
                if len(str_home) > 0 and (home[0] == '' or home[0] == ' '):
                    str_home = ''
                manage = re.findall(pattern_host, row[3])
                host = re.findall(pattern_host, row[3])
                money = re.findall(pattern_money, row[3])
                print("주최 {}".format(host[0]))
                print("주관 {}".format(manage[0]))
                print(date)
                print(datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d'))
                d_start = datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d')
                print(datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d'))
                d_end = datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d')
                print("장소 {}".format(place[0]))
                print("돈 {}".format(money[0]))
                print("폰번호 {}".format(str_phone))
                print("홈페이지 {}".format(str_home))

                query = """insert into refine_schedule
                        (convention_name, event_name, full_address, 
                        place_dept1, place_dept2, place_dept3, date_start, date_end,
                        time_start, time_end, phone_number, home_page, manage, host,
                        money, event_desc, source_url, source_name, reg_date) 
                        values(%s, %s, %s, %s, %s, %s, %s, %s
                        , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                curs.execute(query,
                             ('bexco', match[0],
                              'bexco 부산광역시 해운대구 APEC로 55 {place}'.format(place=place[0]),
                              '부산광역시', '해운대구', 'APEC로 55',
                              d_start, d_end, time_start, time_end,
                              str_phone,
                              str_home, manage[0], host[0], money[0], '',
                              pattern_url, 'bexco', reg_date))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()
