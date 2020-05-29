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
        self.convention_name = 'kakaomap'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'https://map.kakao.com/'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keyword = ['반려동물 훈련소', '반려동물 놀이터']
        for key in keyword:
            self.crawl(key)
        #for row in crawl_results:
        #    self.cm.content_insert(row, 'original')
        self.cm.close()
        self.driver.close()

    def crawl(self, key):
        res = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        now_month = self.now.month
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.find_element_by_xpath('//*[@id="search.keyword.query"]').send_keys(key)
        self.driver.find_element_by_xpath('//*[@id="search.keyword.query"]').send_keys(Keys.ENTER)
        time.sleep(0.5)
        self.driver.find_element_by_xpath('//*[@id="info.search.place.more"]').send_keys(Keys.ENTER)

        length = self.driver.find_element_by_xpath('//*[@id="info.search.place.cnt"]').text
        self.length = int(int(length.replace(',', ''))/15)
        self.length = math.ceil(self.length)+1
        page_cnt = 1
        self.driver.find_element_by_xpath('//*[@id="info.search.page.no1"]').send_keys(Keys.ENTER)
        for page in range(1, self.length + 1):
            content_length = self.driver.find_elements_by_xpath('//*[@id="info.search.place.list"]/li')
            for content in range(1, len(content_length) + 1):
                arr = {}
                try:
                    time.sleep(0.5)
                    dic = {}
                    store_name = self.driver.find_element_by_xpath(
                        '//*[@id="info.search.place.list"]/li[{content}]/div[3]/strong/a[2]'.format(content=content)
                    ).text
                    store_address = self.driver.find_element_by_xpath(
                        '//*[@id="info.search.place.list"]/li[{content}]/div[5]/div[2]/p[1]'.format(content=content)).text
                    store_phone = self.driver.find_element_by_xpath(
                        '//*[@id="info.search.place.list"]/li[{content}]/div[5]/div[4]/span[1]'.format(
                            content=content)).text
                    store_detail = self.driver.find_elements_by_xpath(
                        '//*[@id="info.search.place.list"]/li[{content}]/div[5]/div[4]/a[1]'.format(
                            content=content))
                    event_page_url = store_detail[0].get_attribute('href')
                    print(store_name + ' : ' + store_phone + ' : ' + store_address)
                    arr['store_name'] = store_name
                    arr['store_address'] = store_address
                    arr['store_phone'] = store_phone
                    arr['store_detail'] = event_page_url
                    res.append(arr)
                except NoSuchElementException:
                    continue
            if page != self.length:
                print(page)
                if page_cnt != 5:
                    page_cnt += 1
                    self.driver.find_element_by_xpath('//*[@id="info.search.page.no{}"]'.format(page_cnt)).send_keys(Keys.ENTER)
                else:
                    page_cnt = 1
                    self.driver.find_element_by_xpath('//*[@id="info.search.page.next"]').send_keys(Keys.ENTER)
        save(res, key)


def save(arr, key):
    keyset = {
        '반려동물 훈련소': 'A2232',
        '반려동물 놀이터': 'A2233'
    }
    now = datetime.datetime.now()
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
    file_count = 1
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
        a = '{set}_{word}'.format(set=keyset[key], word=key)
        b = row['store_name']
        c = row['store_name']
        d = row['store_address']
        e = row['store_phone']
        f = date_now
        g = '0'
        h = '카카오지도'
        i = '재사용'
        j = '공개'
        k = '크롤링'
        l = 'http'
        m = row['store_detail']
        n = 'www'
        o = '1'
        p = 'c'
        q = '이준재'
        r = '이준재'
        s = date_now
        t = date_now
        u = '#반려동물, #{}'.format(key)
        insert = (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u)
        ws.append(insert)
        print(insert)
        # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
    wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset[key], word=key))


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
