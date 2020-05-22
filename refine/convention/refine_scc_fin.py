from refine.convention import common as cm
import datetime
import re


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'scc'

    def test_insert1(self):
        cc = cm.CrawlClass()
        rows = cc.content_select(self.convention_name)
        cnt = 0
        for row in rows:
            data = {}
            cnt += 1
            title_setec = r'\"headline\"\>(.*)\<\/h1\>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            # match = re.findall(title_setec, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, row[2])  # 찾아낸 제목에서 키워드로 필터링
            pattern_host = r'주최\/주관\s*\<\/strong\>(.*)\<\/p\>'
            # pattern_manage = r'\"주관사\".*\<\/dt\>\n\<dd\>(.*)\n*\t*\<\/dd\>'
            pattern_date = r'개최기간\s*\<\/strong\>(.*)\<\/p\>'
            pattern_time = r'관람시간\s*\<\/strong\>(.*)\<\/p\>'
            pattern_place = r'개최장소\s*\<\/strong\>(.*)\<\/p\>'
            pattern_money = r'입장료\<\/strong\>(\s*.*\s?.*\s?.*)\<\/p\>'
            pattern_phone = r'전화번호.*\s*([0-9]{2,3}-[0-9]{3,4}-[0-9]{4})'
            pattern_url = row[6]  # 해당 페이지 주소
            pattern_home = r'홈페이지.*\"\>(.*)\<\/a\>'
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            z_start = ''
            z_end = ''
            if match2:
                place = re.findall(pattern_place, row[5])
                if len(place) != 0:
                    str_place = place[0]
                else:
                    str_place = ''
                date = re.findall(pattern_date, row[5])
                tempdate = str(date).replace("\\xa0", "").replace(" ", "").replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = tempdate[0:date_index].replace('.', '-')
                date_end = tempdate[date_index+1:len(tempdate)].replace('.', '-')
                time = re.findall(pattern_time, row[5])
                temptime = str(time).replace("\\xa0", "").replace(" ", "").replace("['", "").replace("']", "").strip()
                time_index = temptime.find('~')
                time_start = temptime[0:time_index]
                time_end = temptime[time_index+1:len(temptime)]
                phone = re.findall(pattern_phone, row[5])
                if len(phone) != 0:
                    str_phone = phone[0].strip()
                else:
                    str_phone = ''
                home = re.findall(pattern_home, row[5])
                if len(home) > 0:
                    str_home = home[0].strip()
                else:
                    str_home = ''
                #manage = re.findall(pattern_manage, row[5])
                #if len(manage) != 0:
                #    str_manage = manage[0].strip()
                #else:
                #    str_manage = ''
                host = re.findall(pattern_host, row[5])
                if len(host) != 0:
                    str_host = host[0]
                else:
                    str_host = ''
                money = re.findall(pattern_money, row[5])
                if len(money) != 0:
                    str_money = money[0]
                else:
                    str_money = ''
                print("주최 {}".format(str_host))
                # print("주관 {}".format(str_manage))
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

                data['convention_name'] = self.convention_name
                data['event_name'] = match2.string
                data['event_type'] = row[3]
                data['place'] = str_place.strip()
                data['date_start'] = d_start
                data['data_end'] = d_end
                data['time_start'] = '-' if time_start == '' else time_start
                data['time_end'] = '-' if time_end == '' else time_end
                data['phone'] = str_phone
                data['home_page'] = str_home
                data['manage'] = str_host.strip()
                data['host'] = str_host.strip()
                data['money'] = str_money.strip()
                data['source_url'] = pattern_url
                data['reg_date'] = reg_date
                cc.content_insert(data)
        cc.commit()
        cc.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()
