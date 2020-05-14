from refine.convention import conn_mysql as cm
import datetime
import re


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'exco'

    def test_insert1(self):
        cc = cm.CrawlClass()
        rows = cc.content_select(self.convention_name)
        cnt = 0
        for row in rows:
            data = {}
            title_exco = r'<span class="\b[^>]*>(.*?)<\/span>'
            title_pattern = r"(캣|도그|펫|동물|애견|애완|파충류|조류|앵무새)"  # row[3] => 페이지소스
            # match = re.findall(title_exco, row[3])  # 제목을 먼저 찾아낸다
            match2 = re.search(title_pattern, row[2])  # 찾아낸 제목에서 키워드로 필터링
            pattern_host = r'주최\s?\<\/td\>\n\<td class\=\"con01\"\>(.*)\<\/td\>' #
            pattern_manage = r'주관\s?\<\/td\>\n\<td class\=\"con01\"\>(.*)\<\/td\>'
            pattern_date = r'\<li\>\<img alt\=\"기간\" src\=\"\/kor\/images\/program\/item\_sch\_01\.gif\"\/\> \<span\>(.*)\<\/span\>' #
            pattern_place = r'\<span\>\n\t*(.*)\n\t*\<\/span\>\<\/li\>' #
            pattern_time = r'\<li\>\<img alt\=\"행사시간\" src\=\"\/kor\/images\/program\/item\_sch\_02\.gif\"\/\> \<span>(.*)\<\/span\>' #
            pattern_money = r'\<li\>\<img alt\=\"입장료\" src\=\"\/kor\/images\/program\/item\_sch\_04.gif\"\/\> \<span\>(.*)\<\/span\>' #
            pattern_phone = r'\<li\>\<img alt\=\"전화\" src\=\"\/kor\/images\/program\/item\_sch\_05.gif\"\/\> \<span\>(.*)\<\/span\>' #
            pattern_url = row[6]  # 해당 페이지 주소
            pattern_home = r'홈페이지\" src\=\"\/kor\/images\/program\/item\_sch\_06\.gif\"\/\>\n\<span\>\n\<a href\=\"(.*)\" style' #
            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
            z_start = ''
            z_end = ''
            if match2:
                cnt += 1
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
                    str_home = home[0].strip()
                else:
                    str_home = ''
                manage = re.findall(pattern_manage, row[5])
                if len(manage) != 0:
                    str_manage = manage[0].strip()
                else:
                    str_manage = ''
                host = re.findall(pattern_host, row[5])
                if len(host) != 0:
                    str_host = host[0].strip()
                else:
                    str_host = ''
                money = re.findall(pattern_money, row[5])
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
                data['manage'] = str_manage
                data['host'] = str_host
                data['money'] = str_money
                data['source_url'] = pattern_url
                data['reg_date'] = reg_date
                cc.content_insert(data)
        cc.commit()
        cc.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()
