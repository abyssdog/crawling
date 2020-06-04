import datetime
import json

import pymysql
import requests


class CrawlClass(object):
    def __init__(self):
        self.conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )

    def pattern_title_animal(self):
        title_pattern = r"(캣|도그|펫|동물|애견|애완|렙타일|곤충)"
        return title_pattern

    def pattern_title_plant(self):
        title_pattern = r"(식물|꽃|화훼|수국|플라워|알리움|로즈|장미|철쭉|야생화|상사화|코스모스|구절초|국향|국화|억새)"
        return title_pattern

    def get_rgn_cd(self, rgn_code):
        dict_rgn = {
            '강원': '033', '경기': '031', '경남': '055',
            '경북': '054', '광주': '062', '대구': '053',
            '대전': '042', '부산': '051', '서울': '02',
            '세종': '044', '울산': '052', '인천': '032',
            '전남': '061', '전북': '063', '제주': '064',
            '충남': '041', '충북': '043',
        }
        rgn_value = dict_rgn['{}'.format(rgn_code)]
        return rgn_value

    def get_address(self, search_word):
        row = {}
        url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(search_word)
        headers = {
            "Authorization": "KakaoAK b3489265c0604b575bc22eda5da2e18f"
        }
        places = requests.get(url, headers=headers).json()['documents']
        for place in places:
            if place['place_name'] == search_word:
                row = {
                    'road_address_name': place['road_address_name'],
                    'x': place['x'],
                    'y': place['y']
                }
        return row

    def get_location(self, addr):
        url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
        headers = {"Authorization": "KakaoAK b3489265c0604b575bc22eda5da2e18f"}
        result = json.loads(str(requests.get(url, headers=headers).text))
        match_first = result['documents'][0]['address']
        print(match_first)
        return float(match_first['y']), float(match_first['x'])

    def get_day_cd(self, date_start, date_end):
        # weekday()  # {0:월, 1:화, 2:수, 3:목, 4:금, 5:토, 6:일}
        day_cd = {
            'all': '둘다',
            'work': '평일',
            'holi': '주말'
        }
        ds = date_start.weekday()
        de = date_end.weekday()
        if ds < 5 and de < 5:
            day_val = 'work'
        elif ds >= 5 and de >= 5:
            day_val = 'holi'
        else:
            day_val = 'all'
        return day_val

    def return_conn(self):
        return self.conn

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def latest_crawl_version(self, convention_name):
        curs = self.conn.cursor()
        sql = """ SELECT crawl_version
                    FROM event_original
                   WHERE convention_name = '{convention_name}'
                   GROUP BY crawl_version
                   ORDER BY crawl_version DESC
                   LIMIT 1
                   """.format(convention_name=convention_name)
        curs.execute(sql)
        rows = curs.fetchall()
        return rows

    def original_select(self, convention_name, crawl_version):
        curs = self.conn.cursor()
        sql = """ SELECT *
                    FROM event_original
                   WHERE convention_name = '{convention_name}' 
        """.format(convention_name=convention_name)
        if crawl_version != 'Null':
            sql += """ AND crawl_version = '{crawl_version}' """.format(crawl_version=crawl_version)
        curs.execute(sql)
        rows = curs.fetchall()
        return rows

    def convention_select(self, data):
        curs = self.conn.cursor()
        sql = """ SELECT *
                    FROM convention
                   WHERE name_en = '{}'
        """.format(data)
        curs.execute(sql)
        rows = curs.fetchall()
        return rows

    def content_insert(self, data):
        curs = self.conn.cursor()
        query = """insert into event_refine
            (convention_name, event_name, event_type, place,  
            date_start, date_end, time_start, time_end, 
            phone, home_page, manage, host, 
            money, source_url, reg_date) 
            values
            (%s, %s, %s, %s, %s, %s, %s, %s,
             %s, %s, %s, %s, %s, %s, %s)
        """
        curs.execute(query,
                     (data['convention_name'], data['event_name'], data['event_type'], data['place'],
                      data['date_start'], data['data_end'], data['time_start'], data['time_end'],
                      data['phone'], data['home_page'], data['manage'], data['host'],
                      data['money'], data['source_url'], data['reg_date']
                      )
                     )
        self.conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.

    def evnt_insert(self, data):
        curs = self.conn.cursor()
        query = """INSERT INTO ma_evnt 
            (TP_CD, PET_CAT_CD, TTL, HOST_NM, SUPVSN,  
            ADDR, ADDR_DTL, LOC, ZIPNO, LAT, LNG, 
            FR_DATE, TO_DATE, EVNT_TIME, ONLN_YN, OFFLN_YN, 
            ENTR_COST, HPG_NM, HPG_URL, QNA, 
            CTN, M_IMG_ID, LIST_IMG_ID,  
            COMP_NM, DAY_CD, RGN_CD,  
            DEL_YN, REG_ID, REG_DTTM, UPD_ID, UPD_DTTM, 
            CRAWL_VERSION, SOURCE_URL, CONVENTION_NAME, EVENT_TYPE
            ) 
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s 
            )
        """
        curs.execute(query,
                     (data['TP_CD'], data['PET_CAT_CD'], data['TTL'], data['HOST_NM'], data['SUPVSN'],
                      data['ADDR'], data['ADDR_DTL'], data['LOC'], data['ZIPNO'], data['LAT'], data['LNG'],
                      data['FR_DATE'], data['TO_DATE'], data['EVNT_TIME'], data['ONLN_YN'], data['OFFLN_YN'],
                      data['ENTR_COST'], data['HPG_NM'], data['HPG_URL'], data['QNA'], data['CTN'],
                      data['M_IMG_ID'], data['LIST_IMG_ID'], data['COMP_NM'], data['DAY_CD'], data['RGN_CD'],
                      data['DEL_YN'], data['REG_ID'], data['REG_DTTM'], data['UPD_ID'], data['UPD_DTTM'],
                      data['CRAWL_VERSION'], data['SOURCE_URL'], data['CONVENTION_NAME'], data['EVENT_TYPE']
                      )
                     )
        self.conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.


if __name__ == '__main__':
    cc = CrawlClass()
    aa = cc.get_address('에버랜드')
    print(aa)
