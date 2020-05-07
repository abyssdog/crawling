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
             WHERE CONVENTION_NAME = 'ceco'
        """
        curs.execute(sql)
        rows = curs.fetchall()
        cnt = 0
        for row in rows:
            cnt += 1
            title_ceco = r'<dd\b[^>]*>(.*?)<\/dd>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            match = re.findall(title_ceco, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            # 여기 아래다가 엑셀 파일에 저장하는걸 만들면 될듯
            pattern_host = r'<span>주최 : (.*?)<\/span\>'
            # pattern_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            pattern_date = r'\<dt\>개최 기간\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_place = r'\<dt\>개최 장소\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_time = r'\<dt\>관람 시간\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_money = r'\<dt\>관람료\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_phone = r'<span>전화번호 : (.*?)<\/span\>'
            pattern_url = row[4]  # 해당 페이지 주소
            pattern_home = r'\<dt\>홈페이지\<\/dt\><dd\>\<a(.*?)\>(.*?)\<\/a\>\<\/dd\>'
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
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
                date_start = tempdate[0:date_index].replace('.', '-')
                date_end = tempdate[date_index+1:len(tempdate)].replace('.', '-')
                time = re.findall(pattern_time, row[3])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                time_index = temptime.find('~')
                time_start = temptime[0:time_index]
                time_end = temptime[time_index+1:len(temptime)]
                phone = re.findall(pattern_phone, row[3])
                if len(phone) != 0:
                    str_phone = phone[0].strip()
                else:
                    str_phone = ''
                home = re.findall(pattern_home, row[3])
                if len(home) > 0:
                    str_home = home[0][1].strip()
                else:
                    str_home = ''
                manage = re.findall(pattern_host, row[3])
                host = re.findall(pattern_host, row[3])
                money = re.findall(pattern_money, row[3])
                if len(money) != 0:
                    str_money = phone[0]
                else:
                    str_money = ''
                print("주최 {}".format(host[0]))
                print("주관 {}".format(manage[0]))
                print(date)
                print(datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d'))
                d_start = datetime.datetime.strptime(date_start.strip(), '%Y-%m-%d')
                print(datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d'))
                d_end = datetime.datetime.strptime(date_end.strip(), '%Y-%m-%d')
                print('{start} ~ {end}'.format(start=time_start, end=time_end))
                print("장소 {}".format(str_place))
                print("돈 {}".format(str_money))
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
                             ('ceco', match[0],
                              'ceco 경상남도 창원시 의창구 원이대로 362 {place}'.format(place=str_place),
                              '창원시', '의창구', '원이대로 362',
                              d_start, d_end, time_start, time_end, str_phone,
                              str_home, manage[0], host[0], str_money, '',
                              pattern_url, 'ceco', reg_date))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()