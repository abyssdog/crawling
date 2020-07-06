import json
import time

import pymysql
import requests

import crawling_googleMap_ranking as cgr
import crawling_kakaoMap_ranking as ckr


class getHospitalData:
    def __init__(self):
        self.key_api = "b3489265c0604b575bc22eda5da2e18f"

    def get_location(self, addr1, addr2):
        b = addr2.find(',')
        if b != -1:
            a2 = addr2[0:b]
        else:
            a2 = addr2
        try:
            url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr1
            headers = {"Authorization": "KakaoAK b3489265c0604b575bc22eda5da2e18f"}
            result = json.loads(str(requests.get(url, headers=headers).text))
            if len(result['documents']) != 0:
                match_first = result['documents'][0]['address']
            else:
                match_first = {
                    'x': 0,
                    'y': 0
                }
        except Exception as e:
            if addr2 != '':
                try:
                    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + a2
                    headers = {"Authorization": "KakaoAK b3489265c0604b575bc22eda5da2e18f"}
                    result = json.loads(str(requests.get(url, headers=headers).text))
                    match_first = result['documents'][0]['address']
                except Exception as e:
                    match_first = {
                        'x': 0,
                        'y': 0
                    }
            else:
                try:
                    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr1
                    headers = {"Authorization": "KakaoAK b3489265c0604b575bc22eda5da2e18f"}
                    result = json.loads(str(requests.get(url, headers=headers).text))
                    match_first = result['documents'][0]['address']
                except Exception:
                    match_first = {
                        'x': 0,
                        'y': 0
                    }
        print(match_first)

        return float(match_first['x']), float(match_first['y'])

    def get_localdata(self):
        conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )
        curs = conn.cursor()
        # business_condition_code = '01' => 정상영업
        sql = """SELECT * FROM animal_hospital
                  WHERE business_condition_code = '01'
                    AND location_x != '0.0'"""
        curs.execute(sql)
        sql_rows = curs.fetchall()
        conn.commit()
        conn.close()
        return sql_rows

    def get_data(self):
        conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )
        curs = conn.cursor()
        # business_condition_code = '01' => 정상영업
        sql = """SELECT * FROM animal_hospital
                  WHERE business_condition_code = '01'
                    AND location_x != '0.0'"""
        curs.execute(sql)
        sql_rows = curs.fetchall()
        conn.commit()
        conn.close()
        return sql_rows

# V call animal_hospital data
# V search kakao map api and save location x,y
# crawling ranking (google) => google map crawling
# crawling operation time (google and naver map)
# save csv
'//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]'
'//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]'

'//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]'
if __name__ == '__main__':
    rows = []
    c = ckr.CrawlClass()
    HD = getHospitalData()
    selected_rows = HD.get_localdata()
    c.run_crawl(selected_rows)
    # selected_rows_added_ranking = c.run_crawl(selected_rows)

    #for row in selected_rows:
    #    xy = HD.get_location(row[18], row[19])
    #    _dict = {"id": row[0], "location_x": xy[0], "location_y": xy[1], 'location_address': row[18], 'road_name_address':row[19]}
    #    rows.append(_dict)
    'https://maps.googleapis.com/maps/api/place/search/xml?location=-33.8670522,151.1957362&radius=500&types=food&name=harbour&sensor=false&key={}'