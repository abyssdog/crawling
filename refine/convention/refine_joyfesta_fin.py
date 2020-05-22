# coding=utf-8
from bs4 import BeautifulSoup as Bs
from refine.convention import common as cm
import datetime
import re
import urllib.request


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'joyfesta'
        self.now = datetime.datetime.now()

    def encode_url(self, encode_list):
        url_text = ''
        for encode in encode_list:
            url_text += encode
        a = url_text.encode("idna")
        return a

    def insert(self):
        cc = cm.CrawlClass()
        crawl_version = self.now.strftime('%Y%m%d')
        rows = cc.original_select(self.convention_name, crawl_version)
        # convention_info = cc.convention_select(self.convention_name)
        for row in rows:
            data = {}
            animal = re.search(cc.pattern_title_animal(), row[2])
            plant = re.search(cc.pattern_title_plant(), row[2])
            if animal is not None:
                pet_cat_cd = 'animal'
                match = animal
            elif plant is not None:
                pet_cat_cd = 'plant'
                match = plant
            else:
                pet_cat_cd = ''
                match = False
            pattern_addr = r'위치\<\/th\>\s*\<td\>(.*)\<\/td\>'
            pattern_addr_dtl = r'행사장소\<\/th\>\s*\<td\>(.*)\<\/td\>'
            pattern_cost = r'입장료\<\/th\>\s*\<td\>(.*)\s*\<\/td\>'
            pattern_date = r'행사기간\<\/th\>\s*\<td\>(.*)\<\/td\>'
            pattern_home = r'홈페이지\<\/th\>\s*\<td\>.*\_blank\"\>(.*)\<\/a\>\<\/td\>'
            pattern_host = r'주최\<\/th\>\s*\<td\>(.*)\<\/td\>'
            pattern_phone = r'연락처\<\/th\>\s*\<td\>.*\"\>(.*)\<\/a\>\<\/td\>'
            pattern_supvsn = r'주관\<\/th\>\s*\<td\>(.*)\<\/td\>'
            pattern_time = r'\<dt\>시간\<\/dt\>\n\<dd\>(.*?)\<\/dd\>'
            # pattern_ctn = r''
            reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
            source_url = row[7]
            insert_flag = True
            if match:
                host = re.findall(pattern_host, row[5])
                if len(host) > 0:
                    str_host = host[0]
                else:
                    str_host = ''
                supvsn = re.findall(pattern_supvsn, row[5])
                if len(supvsn) > 0:
                    str_supvsn = supvsn[0]
                else:
                    str_supvsn = ''
                addr = re.findall(pattern_addr, row[5])
                if len(addr) > 0:
                    str_addr = addr[0]
                else:
                    str_addr = ''

                addt_dtl = re.findall(pattern_addr_dtl, row[5])
                if len(addt_dtl) > 0:
                    str_addt_dtl = addt_dtl[0]
                else:
                    str_addt_dtl = ''
                date = re.findall(pattern_date, row[5])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = datetime.datetime.strptime(tempdate[0:date_index].replace('.', '-').strip(), '%Y-%m-%d')
                date_end = datetime.datetime.strptime(
                    tempdate[date_index+1:len(tempdate)].replace('.', '-').strip(), '%Y-%m-%d')
                temp_time = re.findall(pattern_time, row[5])
                if len(temp_time) > 0:
                    str_time = temp_time[0]
                else:
                    str_time = ''
                cost = re.findall(pattern_cost, row[5])
                if len(cost) > 0:
                    str_cost = cost[0]
                else:
                    str_cost = ''
                phone = re.findall(pattern_phone, row[5])
                if len(phone) > 0:
                    str_phone = phone[0]
                else:
                    str_phone = ''

                home = re.findall(pattern_home, row[5])
                if len(home) > 0 and home[0] != '':
                    pattern_hangul = r'[가-힣]'
                    hangul = re.findall(pattern_hangul, home[0])
                    if len(hangul) > 0:
                        str_home_url = home[0]
                        pre_url = home[0][0:home[0].index(hangul[0])]
                        sub_url = home[0][home[0].index(hangul[len(hangul)-1])+1:len(home[0])]
                        encode_url1 = self.encode_url(hangul)
                        str_home_url = str(encode_url1)[2:len(str(encode_url1))-1] + sub_url
                        res = urllib.request.urlopen(pre_url + str_home_url)

                        soup = Bs(res, 'html.parser')
                        home_title = soup.select('head > title')
                        str_home_title = home_title[0].text if len(home_title) > 0 else ''
                    else:
                        str_home_url = home[0]
                        res = urllib.request.urlopen(str_home_url).read()

                        soup = Bs(res, 'html.parser')
                        home_title = soup.select('head > title')
                        str_home_title = home_title[0].text if len(home_title) > 0 else ''
                else:
                    str_home_url = ''
                    str_home_title = ''

                if match.string[0:1] == '[':
                    insert_flag = False
                else:
                    str_rgn_cd = '9999'

                if insert_flag:
                    print(match.string)
                    data['TP_CD'] = 'fest'
                    data['PET_CAT_CD'] = pet_cat_cd
                    data['TTL'] = match.string
                    data['HOST_NM'] = str_host
                    data['SUPVSN'] = str_supvsn
                    data['ADDR'] = str_addr
                    data['ADDR_DTL'] = str_addt_dtl
                    data['LOC'] = str_addt_dtl
                    data['ZIPNO'] = ''
                    data['LAT'] = 0
                    data['LNG'] = 0
                    data['FR_DATE'] = date_start
                    data['TO_DATE'] = date_end
                    data['EVNT_TIME'] = str_time
                    data['ONLN_YN'] = 'N'
                    data['OFFLN_YN'] = 'Y'
                    data['ENTR_COST'] = str_cost
                    data['HPG_NM'] = str_home_title
                    data['HPG_URL'] = str_home_url
                    data['QNA'] = str_phone
                    data['CTN'] = row[6] if row[6] is not None else ''
                    data['M_IMG_ID'] = row[8] if row[8] is not None else ''
                    data['LIST_IMG_ID'] = ''
                    data['COMP_NM'] = str_host
                    data['DAY_CD'] = cc.get_day_cd(date_start, date_end)
                    data['RGN_CD'] = str_rgn_cd
                    data['DEL_YN'] = 'N'
                    data['REG_ID'] = 'crawler'
                    data['REG_DTTM'] = reg_date
                    data['UPD_ID'] = 'crawler'
                    data['UPD_DTTM'] = reg_date
                    data['CRAWL_VERSION'] = crawl_version
                    data['SOURCE_URL'] = source_url
                    data['CONVENTION_NAME'] = self.convention_name
                    data['EVENT_TYPE'] = row[3] if row[3] is not None else ''
                    cc.evnt_insert(data)
        cc.commit()
        cc.close()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.insert()
