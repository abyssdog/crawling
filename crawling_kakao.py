import datetime
import math

import requests
from openpyxl import Workbook


class kakao_api:
    def __init__(self):
        self.url = "https://dapi.kakao.com/v2/search/{}"
        self.key_api = "cdcc207699aa560ad8ee2704ec344af5"
        # self.total_count = 0
        # self.pageable_count = 0
        # self.is_end = True

    def run(self, key_search):
        ka = kakao_api()
        flags = ['cafe', 'blog']
        for flag in flags:
            total = ka.get_total_count(key_search, flag)
            ka.get_content(key_search, total, flag)

    def get_total_count(self, key_search, flag):
        response = requests.get(self.url.format(flag),
                                params={'query': key_search, 'sort': 'recency'},
                                headers={'Authorization': 'KakaoAK ' + self.key_api}
                                )
        if response.status_code == 200:
            meta_info = response.json()['meta']
            re = {
                'total_count': meta_info['total_count'],
                'pageable_count': meta_info['pageable_count'],
                'is_end': meta_info['is_end']
            }
            print(re)
            return re

    def get_content(self, key_search, total, flag):
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        wb = Workbook()
        ws = wb.active
        ws.append(('ID', '{}_title'.format(flag), '{}_summary'.format(flag),
                   '{}_url'.format(flag), '{}_name'.format(flag), '{}_datetime'.format(flag)))
        total_pages = math.ceil(total['pageable_count']/10) if total['pageable_count']/10 <= 50 else 50
        cnt = 0
        for page_count in range(1, total_pages+1):
            response = requests.get(self.url.format(flag),
                                    params={'query': key_search, 'page': page_count, 'sort': 'recency'},
                                    headers={'Authorization': 'KakaoAK ' + self.key_api}
                                    )
            for row in response.json()["documents"]:
                cnt += 1
                a = cnt
                b = row['title']
                c = row['contents']
                d = row['url']
                e = row['{}name'.format(flag)]
                f = row['datetime']
                insert = (a, b, c, d, e, f)
                ws.append(insert)
                print(page_count)
        wb.save('C:/workSpace/flask_crawling/originalDatas/kakao_{}_api_test.xlsx'.format(flag))


if __name__ == '__main__':
    k = kakao_api()
    k.run('반려동물')
