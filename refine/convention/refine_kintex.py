import datetime
from datetime import timedelta
import pymysql
import re
from openpyxl import Workbook
from openpyxl import load_workbook


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
             WHERE CONVENTION_NAME = 'kintex'
        """
        curs.execute(sql)
        rows = curs.fetchall()
        cnt = 0
        for row in rows:
            cnt += 1
            title_kintex = r'\".*\n\t* *(.*)\n\t*\<\/h4\>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            match = re.findall(title_kintex, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            pattern_host = r'\"주최\".*\<\/dt\>\n\<dd\>(.*)\<\/dd\>' #
            pattern_manage = r'\"주관사\".*\<\/dt\>\n\<dd\>(.*)\n*\t*\<\/dd\>' #
            pattern_date = r'\"기간\".*\<\/dt\>\n\<dd\>(.*)\<\/dd\>' #
            pattern_time = r'\"관람시간\".*\<\/dt\>\n\<dd\>(.*)\<\/dd\>' #
            pattern_place = r'\"장소\".*\<\/dt\>\n\<dd\>\n* *(.*)\n*\t*.*\n\<\/dd\>' #
            pattern_money = r'\"입장료\".*\<\/dt\>\n\<dd\>(.*)\<\/dd\>' #
            pattern_phone = r'\"전화번호\".*\<\/dt\>\n\<dd\>\n*(.*)\n*\t*\<\/dd\>' #
            pattern_url = row[4]  # 해당 페이지 주소
            pattern_home = r'\"홈페이지\".*\<\/dt\>\n\<dd\>\n\<a.*\>(.*)\<\/a\>' #
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            z_start = ''
            z_end = ''
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
                    str_home = home[0].strip()
                else:
                    str_home = ''
                manage = re.findall(pattern_manage, row[3])
                if len(manage) != 0:
                    str_manage = manage[0].strip()
                else:
                    str_manage = ''
                host = re.findall(pattern_host, row[3])
                if len(host) != 0:
                    str_host = host[0]
                else:
                    str_host = ''
                money = re.findall(pattern_money, row[3])
                if len(money) != 0:
                    str_money = money[0]
                else:
                    str_money = ''
                print("주최 {}".format(str_host))
                print("주관 {}".format(str_manage))
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
                executed = curs.execute(query,
                                        ('kintex', match[0],
                                         'kintex 경기도 고양시 일산서구 킨텍스로 217-60  {place}'.format(place=str_place),
                                         '고양시', '일산서구', '킨텍스로 217-60',
                                         d_start, d_end, time_start, time_end,
                                         str_phone,
                                         str_home, str_manage, str_host, str_money, '',
                                         pattern_url, 'kintex', reg_date))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()