# from bs4 import BeautifulSoup as Bs
from refine.convention import common as cm
import datetime
import re
# import urllib.request


class CrawlClass(object):
    def __init__(self):
        self.convention_name = 'dcc'
        self.now = datetime.datetime.now()

    def refine(self):
        cc = cm.CrawlClass()
        crawl_version = self.now.strftime('%Y%m%d')
        rows = cc.original_select(self.convention_name, crawl_version)
        convention_info = cc.convention_select(self.convention_name)

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

            pattern_host = r'\"주최자\".*\n*.*\n*.*\"txtcheck\"\>(.*)\<\/td\>'
            # pattern_supvsn = r'주관\<\/th\>\n\<td\>[\n\t ]*(.*)[\n\t ]*\<\/td\>'
            pattern_addt_dtl = r'\"행사장소\".*\n*.*\n*.*\"txtcheck\"\>(.*)\<\/td\>'
            pattern_date = r'\"행사기간\".*\n*.*\n*.*\"txtdate\"\>(.*)\<\/td\>'
            pattern_time = r'\"행사시간\".*\n*.*\n*.*\"txtdate\"\>(.*)\<\/td\>'
            # pattern_cost = r'입장료\<\/th\>\n\<td\>(.*)\<\/td\>'
            # pattern_phone = r'문의처\<\/th\>\n\<td\>(.*)\<\/td\>'
            # pattern_home = r'행사홈페이지\<\/th\>\n.*\<a.*\>(.*)\<\/a\>'
            # pattern_ctn = r''
            reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
            source_url = row[7]

            if match:
                host = re.findall(pattern_host, row[5])
                if len(host) > 0:
                    str_host = host[0]
                else:
                    str_host = ''
                # supvsn = re.findall(pattern_supvsn, row[5])
                # if len(supvsn) > 0:
                #     str_supvsn = supvsn[0]
                # else:
                #     str_supvsn = ''
                addt_dtl = re.findall(pattern_addt_dtl, row[5])
                if len(addt_dtl) > 0:
                    str_addt_dtl = addt_dtl[0]
                else:
                    str_addt_dtl = ''
                date = re.findall(pattern_date, row[5])
                tempdate = str(date).replace("['", "").replace("']", "").strip()
                date_index = tempdate.find('~')
                date_start = datetime.datetime.strptime(
                    tempdate[0:date_index].replace('/', '-').strip(), '%Y-%m-%d')
                date_end = datetime.datetime.strptime(
                    tempdate[date_index + 1:len(tempdate)].replace('/', '-').strip(), '%Y-%m-%d')
                time = re.findall(pattern_time, row[5])
                if len(time) > 0:
                    str_time = time[0]
                else:
                    str_time = ''
                '''cost = re.findall(pattern_cost, row[5])
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
                if len(home) > 0:
                    str_home_url = home[0]
                    res = urllib.request.urlopen(str_home_url).read()
                    soup = Bs(res, 'html.parser')
                    home_title = soup.select('head > title')
                    str_home_title = home_title[0].text
                else:
                    str_home_url = ''
                    str_home_title = '''''

                data['TP_CD'] = 'fest'
                data['PET_CAT_CD'] = pet_cat_cd
                data['TTL'] = match.string
                data['HOST_NM'] = str_host
                data['SUPVSN'] = str_host
                data['ADDR'] = convention_info[0][4]
                data['ADDR_DTL'] = str_addt_dtl
                data['LOC'] = self.convention_name
                data['ZIPNO'] = convention_info[0][6]
                data['LAT'] = convention_info[0][7]
                data['LNG'] = convention_info[0][8]
                data['FR_DATE'] = date_start
                data['TO_DATE'] = date_end
                data['EVNT_TIME'] = str_time
                data['ONLN_YN'] = 'N'
                data['OFFLN_YN'] = 'Y'
                data['ENTR_COST'] = ''
                data['HPG_NM'] = ''
                data['HPG_URL'] = ''
                data['QNA'] = ''
                data['CTN'] = row[6] if row[6] is not None else ''
                data['M_IMG_ID'] = row[8] if row[8] is not None else ''
                data['LIST_IMG_ID'] = ''
                data['COMP_NM'] = str_host
                data['DAY_CD'] = cc.get_day_cd(date_start, date_end)
                data['RGN_CD'] = cc.get_rgn_cd(convention_info[0][4][0:2])
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
    crawl.refine()
