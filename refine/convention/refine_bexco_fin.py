from refine.convention import conn_mysql as cm
import datetime
import pymysql
import re


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'bexco'

    def test_insert1(self):
        cc = cm.CrawlClass()
        rows = cc.content_select(self.convention_name)
        cnt = 0
        for row in rows:
            data = {}
            title_bexco = r"<h3\b[^>]*>(.*?)<\/h3>"
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            # match = re.findall(title_bexco, row[3])  # 제목을 먼저 찾아낸다
            # match2 = re.search(title_pattern, match[0])  # 찾아낸 제목에서 키워드로 필터링
            match2 = re.search(title_pattern, row[2])  # 찾아낸 제목에서 키워드로 필터링
            # 여기 아래다가 엑셀 파일에 저장하는걸 만들면 될듯
            pattern_host = r'\<dt\>주최\/주관\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            # pattern_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            pattern_date = r'\<dt\>기간<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_place = r'\<dt\>장소\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_time = r'\<dt\>시간\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_money = r'\<dt\>관람료\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_phone = r'\<dt\>전화\<\/dt\>\n\<dd\>\n\t{4}(.*?)\n\t{4}\<\/dd\>'
            pattern_url = row[6]  # 해당 페이지 주소
            pattern_home = r'\<dt\>홈페이지\<\/dt\>\n\<dd\>\n\t{4}(.*?)\n\t{4}\<\/dd\>'
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')

            if match2:
                cnt += 1
                place = re.findall(pattern_place, row[5])
                date = re.findall(pattern_date, row[5])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = tempdate[0:date_index].replace('.', '-')
                date_end = tempdate[date_index+1:len(tempdate)].replace('.', '-')
                time = re.findall(pattern_time, row[5])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                time_index = temptime.find('~')
                time_start = temptime[0:time_index]
                time_end = temptime[time_index+1:len(temptime)]
                phone = re.findall(pattern_phone, row[5])
                str_phone = phone[0].strip()
                if phone[0] == '-- ' or phone[0] == ' ':
                    str_phone = ''
                home = re.findall(pattern_home, row[5])
                if len(home) > 0:
                    str_home = home[0].strip()
                else:
                    str_home = ''
                if len(str_home) > 0 and (home[0] == '' or home[0] == ' '):
                    str_home = ''
                manage = re.findall(pattern_host, row[5])
                host = re.findall(pattern_host, row[5])
                money = re.findall(pattern_money, row[5])
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

                data['convention_name'] = self.convention_name
                data['event_name'] = match2.string
                data['event_type'] = row[3]
                data['place'] = place[0]
                data['date_start'] = d_start
                data['data_end'] = d_end
                data['time_start'] = time_start
                data['time_end'] = time_end
                data['phone'] = phone[0]
                data['home_page'] = str_home
                data['manage'] = manage[0]
                data['host'] = host[0]
                data['money'] = money[0]
                data['source_url'] = pattern_url
                data['reg_date'] = reg_date
                cc.content_insert(data)
        cc.commit()
        cc.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()
