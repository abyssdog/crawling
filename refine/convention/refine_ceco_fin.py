from refine.convention import common as cm
import datetime
import re


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'ceco'

    def test_insert1(self):
        cc = cm.CrawlClass()
        rows = cc.content_select(self.convention_name)
        cnt = 0
        for row in rows:
            data = {}
            cnt += 1
            title_ceco = r'<dd\b[^>]*>(.*?)<\/dd>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완)"  # row[3] => 페이지소스
            # match = re.findall(title_ceco, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, row[2])  # 찾아낸 제목에서 키워드로 필터링
            # 여기 아래다가 엑셀 파일에 저장하는걸 만들면 될듯
            pattern_host = r'<span>주최 : (.*?)<\/span\>'
            # pattern_manage = r'<li><span class="tit">주관<\/span>(.*?)<\/li>'
            pattern_date = r'\<dt\>개최 기간\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_place = r'\<dt\>개최 장소\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_time = r'\<dt\>관람 시간\<\/dt\><dd\>(.*?)<\/dd\>'
            pattern_money = r'\<dt\>관람료\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            pattern_phone = r'<span>전화번호 : (.*?)<\/span\>'
            pattern_url = row[6]  # 해당 페이지 주소
            pattern_home = r'\<dt\>홈페이지\<\/dt\><dd\>\<a(.*?)\>(.*?)\<\/a\>\<\/dd\>'
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            if match2:
                place = re.findall(pattern_place, row[5])
                if len(place) != 0:
                    str_place = place[0]
                else:
                    str_place = ''
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
                if len(phone) != 0:
                    str_phone = phone[0].strip()
                else:
                    str_phone = ''
                home = re.findall(pattern_home, row[5])
                if len(home) > 0:
                    str_home = home[0][1].strip()
                else:
                    str_home = ''
                manage = re.findall(pattern_host, row[5])
                host = re.findall(pattern_host, row[5])
                money = re.findall(pattern_money, row[5])
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
