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
        self.url_a = 'http://webtoon.daum.net/search/total?q=%EB%8F%99%EB%AC%BC#page={page}'
        self.url_base = 'http://webtoon.daum.net{}'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keyword = ['반려동물']
        for key in keyword:
            a = self.crawl(key)
            b = self.append(a)
            self.save(b, key)
        self.cm.close()
        self.driver.close()

    def crawl(self, key):
        res = []
        # 올해 년도 구하기
        now_month = self.now.strftime('%m')
        now_month = self.now.month
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        self.driver.maximize_window()
        cnt = 0
        while True:
            cnt += 1
            self.driver.get(self.url_a.format(page=cnt))
            self.driver.refresh()
            time.sleep(0.5)

            length = self.driver.find_elements_by_xpath('//*[@id="resultList"]/li')
            if len(length) == 0:
                break
            for content in range(1, len(length)+1):
                arr = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="resultList"]/li[{content}]/div/strong/a'.format(content=content)
                )
                webtoon_url = href_tag[0].get_attribute('href')
                webtoon_name = href_tag[0].text
                webtonn_artists = self.driver.find_elements_by_xpath('//*[@id="resultList"]/li[{content}]/div/dl/dd[2]/a'.format(content=content))
                if len(webtonn_artists) > 1:
                    gum = '글작가:{}'.format(webtonn_artists[0].text)
                    gurim = '그림작가:{}'.format(webtonn_artists[1].text)
                    arr['webtoon_artist'] = gum+', '+gurim
                else:
                    arr['webtoon_artist'] = '작가:{}'.format(webtonn_artists[0].text)
                arr['webtoon_url'] = webtoon_url
                arr['webtoon_name'] = webtoon_name

                res.append(arr)
        return res

    def append(self, arr):
        for inlist in arr:
            self.driver.get(inlist['webtoon_url'])
            pattern_url = r'league'
            flag = re.search(pattern_url, inlist['webtoon_url'])
            if flag:
                time.sleep(2)
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')

                page_source = self.soup.select('#cSub > div > div.bg_comm.product_detail > span.txt_story')
                pattern_ctn = r'txt_story\"\s?title\=\".*\"\>(.*)\<\/span\>'
                ctn = re.findall(pattern_ctn, str(page_source))
                if len(ctn) == 0:
                    time.sleep(2)
                    inlist['webtoon_ctn'] = self.driver.find_element_by_xpath(
                        '//*[@id="cSub"]/div/div[2]/span[2]').text
                else:
                    print(ctn[0])
                    inlist['webtoon_ctn'] = ctn[0]
            else:
                time.sleep(2)
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')

                page_source = self.soup.select('#cSub > div.product_info > div > div > dl')
                pattern_ctn = r'txt_story\"\>(.*)\<\/dd\>'
                ctn = re.findall(pattern_ctn, str(page_source))
                if len(ctn) == 0:
                    time.sleep(2)
                    inlist['webtoon_ctn'] = self.driver.find_element_by_xpath('//*[@id="cSub"]/div[1]/div/div/dl/dd[2]').text
                else:
                    print(ctn[0])
                    inlist['webtoon_ctn'] = ctn[0]
        return arr

    def save(self, arr, key):
        keyset = {
            '반려동물 웹툰': 'A2384'
        }
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        wb = Workbook()
        ws = wb.active
        # 첫행 입력
        ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
                   '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
                   '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드'))
        # DB 모든 데이터 엑셀로
        cnt = 0
        for row in arr:
            cnt += 1
            a = '{set}_{word}'.format(set=keyset['{} 웹툰'.format(key)], word=str(cnt).zfill(4))
            b = row['webtoon_name']
            c = '다음 웹툰'
            d = row['webtoon_ctn']
            e = row['webtoon_artist']
            f = date_now
            g = '0'
            h = '다음 웹툰'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = self.url_base.format(row['webtoon_url'])
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#{key}, #웹툰, #{key} 웹툰'.format(key=key)
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['{} 웹툰'.format(key)], word=key+' 웹툰'))
        

if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
