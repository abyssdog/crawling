from refine.convention import conn_mysql as cm
import datetime
import pymysql
import re


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'atcenter'
        self.now = datetime.datetime.now()

    def insert(self):
        cc = cm.CrawlClass()
        rows = cc.content_select(self.convention_name)
        crawl_version = self.now.strftime('%Y%m%d')
        cnt = 0
        for row in rows:
            data = {}
            cnt += 1
            title_atpattern = r"<th\b[^>]*>(.*?)<\/th>"
            title_pattern = r"(캣|도그|펫|동물|애견|애완|교육|자격증|훈련)"  # row[3] => 페이지소스
            #match = re.findall(title_atpattern, row[2])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, row[2])  # 찾아낸 제목에서 키워드로 필터링
            at_host = r'<li><span class="tit">주최<\/span>(.*?)<\/li>'
            at_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            at_date = r'<li><span class="tit">기간<\/span>(.+)<\/li>'
            at_place = r'<li><span class="tit">장소<\/span>(.*?)<\/li>'
            at_time = r'시간\<\/span\>[\n\t ]*(.*)[\n\t ]*\<\/li\>'
            at_money = r'<li><span class="tit">입장료<\/span>(.*?)<\/li>'
            at_phone = r'<li><span class="tit">행사문의<\/span>(.*?)<\/li>'
            at_url = row[6]  # 해당 페이지 주소
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            pattern_home = r'홈페이지\<\/span\>\n\<a href\=\".*\"\>(.*)\<\/a\>'
            z_start = ''
            z_end = ''
            if match2:
                print(match2)  # title
                host = re.findall(at_host, row[5])
                manage = re.findall(at_manage, row[5])
                date = re.findall(at_date, row[5])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                at_index = tempdate.find('-')
                at_start = tempdate[0:at_index].replace('.', '-')
                at_end = tempdate[at_index+2:len(tempdate)].replace('.', '-')
                place = re.findall(at_place, row[5])
                time = re.findall(at_time, row[5])
                temptime = str(time).replace("['", "").replace("']", "").strip()
                at_t_index = temptime.find('-')
                time_start = temptime[0:at_t_index]
                time_end = temptime[at_t_index+2:len(temptime)]
                money = re.findall(at_money, row[5])
                phone = re.findall(at_phone, row[5])
                home = re.findall(pattern_home, row[5])
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
                    print("시간 {}".format(time_start))
                    print("시간 {}".format(time_end))
                    print("돈 {}".format(money[0]))
                    print("번호 {}".format(phone[0]))
                    print("홈페이지 {}".format(str_home))
                    z_start = datetime.datetime.strptime(at_start.strip(), '%Y-%m-%d')
                    z_end = datetime.datetime.strptime(at_end.strip(), '%Y-%m-%d')
                except ValueError:
                    if at_end == '2004--':
                        z_end = datetime.datetime.strptime("2004-03-07", '%Y-%m-%d')
                data['convention_name'] = self.convention_name
                data['event_name'] = match2.string
                data['event_type'] = row[3]
                data['place'] = place[0]
                data['date_start'] = z_start
                data['data_end'] = z_end
                data['time_start'] = time_start
                data['time_end'] = time_end
                data['phone'] = phone[0]
                data['home_page'] = str_home
                data['manage'] = manage[0]
                data['host'] = host[0]
                data['money'] = money[0]
                data['source_url'] = at_url
                data['reg_date'] = reg_date
                data['crawl_version'] = crawl_version
                cc.content_insert(data)
        cc.commit()
        cc.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.insert()