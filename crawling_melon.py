import math

from bs4 import BeautifulSoup as Bs
from selenium.webdriver.common.keys import Keys

from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import calendar
import datetime
import os
import re
import time
from openpyxl import Workbook
from selenium.common.exceptions import NoSuchElementException


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url_a = 'https://www.melon.com/search/album/index.htm?q=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC&section=album' \
                   '&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form'
        self.album_url = 'https://www.melon.com/album/detail.htm?albumId={}'
        self.url_p = 'https://www.melon.com/search/album/index.htm?q=%EC%8B%9D%EB%AC%BC&section=album&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keyword = ['식물']
        for key in keyword:
            a = self.crawl(key)
            b = self.append(a)
            self.save(b, key)
        self.cm.close()
        self.driver.close()

    def crawl(self, key):
        res = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        # now_month = self.now.month
        # reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        print(key)
        if key == '반려동물':
            self.driver.get(self.url_a)
        else:
            self.driver.get(self.url_p)
        self.driver.maximize_window()

        length = self.driver.find_element_by_xpath('//*[@id="conts"]/div[3]/h3/strong/em').text
        self.length = int(int(length.replace(',', ''))/21)
        self.length = math.ceil(self.length)+1
        for page in range(1, self.length + 1):
            time.sleep(0.5)
            content_length = self.driver.find_elements_by_xpath('//*[@id="frm"]/div/ul/li')
            for content in range(1, len(content_length) + 1):
                arr = {}
                time.sleep(0.5)
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="frm"]/div/ul/li[{content}]/div/div/dl/dt/a'.format(content=content)
                )
                album_url = href_tag[0].get_attribute('href')
                pattern_url = r'goAlbumDetail\(\'([0-9]*)\'\)\;'
                url = re.findall(pattern_url, album_url)
                album_name = href_tag[0].text
                try:
                    album_artist = self.driver.find_element_by_xpath(
                        '//*[@id="frm"]/div/ul/li[{content}]/div/div/dl/dd[1]/div/a'.format(content=content)).text
                except NoSuchElementException:
                    album_artist = self.driver.find_element_by_xpath(
                        '//*[@id="frm"]/div/ul/li[{content}]/div/div/dl/dd[1]/div'.format(content=content)).text
                album_date = self.driver.find_element_by_xpath(
                    '//*[@id="frm"]/div/ul/li[{content}]/div/div/dl/dd[3]/span[1]'.format(content=content)).text
                arr['album_url'] = url[0]
                arr['album_name'] = album_name
                print(album_name)
                arr['album_artist'] = album_artist
                arr['album_date'] = album_date
                res.append(arr)

            if page != self.length:
                self.cnt += 21
                self.driver.execute_script("javascript: pageObj.sendPage('{}');".format(self.cnt))
        # save(res, key)
        return res

    def append(self, lis):
        relist = []
        for inlist in lis:
            self.driver.get(self.album_url.format(inlist['album_url']))
            time.sleep(2)
            sing_list = self.driver.find_elements_by_xpath('//*[@id="frm"]/div/table/tbody/tr')
            for sing in range(1, len(sing_list)+1):
                redict = {}
                try:
                    redict['sing_name'] = self.driver.find_element_by_xpath('//*[@id="frm"]/div/table/tbody/tr[{sing}]/td[4]/div/div/div[1]/span/a'.format(sing=sing)).text
                except NoSuchElementException:
                    continue
                redict['album_planner'] = self.driver.find_element_by_xpath('//*[@id="conts"]/div[2]/div/div[2]/div[2]/dl/dd[4]').text
                redict['album_name'] = inlist['album_name']
                redict['album_artist'] = inlist['album_artist']
                redict['album_url'] = self.album_url.format(inlist['album_url'])
                redict['album_date'] = inlist['album_date']
                redict['album_publisher'] = self.driver.find_element_by_xpath('//*[@id="conts"]/div[2]/div/div[2]/div[2]/dl/dd[3]').text
                relist.append(redict)
        return relist

    def save(self, arr, key):
        keyset = {
            '반려동물 뮤직': 'A2381',
            '반려식물 뮤직': 'P2381'
        }
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        wb = Workbook()
        ws = wb.active
        # 첫행 입력
        ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
                   '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
                   '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드', '가변필드 메타명', '추가필드#1', '추가필드#2'))
        # DB 모든 데이터 엑셀로
        cnt = 0
        for row in arr:
            cnt += 1
            if key == '반려동물':
                a = '{set}_{word}'.format(set=keyset['{} 뮤직'.format(key)], word=str(cnt).zfill(4))
                u = '#{key}, #뮤직, #{key} 뮤직'.format(key=key)
            else:
                a = '{set}_{word}'.format(set=keyset['반려{} 뮤직'.format(key)], word=str(cnt).zfill(4))
                u = '#반려{key}, #뮤직, #반려{key} 뮤직'.format(key=key)
            b = row['sing_name']
            c = row['album_planner']
            d = row['album_name']
            e = row['album_artist']
            f = date_now
            g = '0'
            h = '멜론'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = row['album_url']
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now

            v = '@{fir}, @{sec}'.format(fir='발매일', sec='발매사')
            w = row['album_date']
            x = row['album_planner']
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u, v, w, x)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        if key == '반려동물':
            wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['{} 뮤직'.format(key)], word=key+' 뮤직'))
        else:
            wb.save(
                'C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['반려{} 뮤직'.format(key)],
                                                                                     word='반려{} 뮤직'.format(key)))


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
