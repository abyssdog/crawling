import json
import time

import pymysql
import requests


class kakao_api:
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
        ka = kakao_api()
        rows = []
        conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )
        curs = conn.cursor()
        sql = """SELECT id, company_name, location_address, road_name_address
                       FROM animal_sales"""
        curs.execute(sql)
        sql_rows = curs.fetchall()
        for row in sql_rows:
            xy = ka.get_location(row[2], row[3])
            _dict = {"id": row[0], "location_x": xy[0], "location_y": xy[1]}
            rows.append(_dict)
        for row in rows:
            sql = """update animal_funeral
                        set location_x = {x}, location_y = {y}
                      where id = {id}""".format(x=row['location_x'], y=row['location_y'], id=row['id'])
            curs.execute(sql)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    k = kakao_api()
    # k.get_localdata()
    a = k.get_location('우리집막내둥이', '')
    print(a)
