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

    def run_crawl(self, selected_list):
        keyword = ['동물병원']
        result = self.crawl(selected_list)
        self.save(result)
        #for row in crawl_results:
        #    self.cm.content_insert(row, 'original')
        self.cm.close()
        self.driver.close()

    def compare_with_address(self, address_location, address_road, address_target):
        ar = address_road.split()
        al = address_location.split()
        at = address_target.split()
        cnt = 0
        for word in ar:
            if word in at:
                cnt += 1
        if len(ar) == cnt:
            return True
        else:
            for word in al:
                if word in at:
                    cnt += 1
            if len(al) == cnt:
                return True
            else:
                return False

    def get_data(self, target):
        target_address_road = self.driver.find_element_by_xpath(
            '//*[@id="info.search.place.list"]/li[{target}]/div[5]/div[2]/p[1]'.format(target=target)).text
        target_open_hour = self.driver.find_element_by_xpath(
            '//*[@id="info.search.place.list"]/li[{target}]/div[5]/div[3]/p/a'.format(target=target)).text
        target_ranking = self.driver.find_element_by_xpath(
            '//*[@id="info.search.place.list"]/li[{target}]/div[4]/span[1]/em'.format(target=target)).text
        target_phone = self.driver.find_element_by_xpath(
            '//*[@id="info.search.place.list"]/li[{target}]/div[5]/div[4]/span[1]'.format(target=target)).text
        target_url = self.driver.find_elements_by_xpath(
            '//*[@id="info.search.place.list"]/li[{target}]/div[5]/div[4]/a[1]'.format(target=target))
        target_page_url = target_url[0].get_attribute('href')
        return {
            'address_road': target_address_road,
            'open_hour': target_open_hour,
            'ranking': target_ranking,
            'phone': target_phone,
            'url': target_page_url
        }

    def crawl(self, selected_list):
        res = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        now_month = self.now.month
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        self.driver.get(self.url)
        self.driver.maximize_window()
        # row 는 tuple
        for row in selected_list:
            crawled_data = {}
            # set search keyword
            address_location = row[18].split()
            temp = row[19].split(',')
            address_road = temp[0].split()
            search_keyword = address_location[0]+' '+address_location[1]+' '+row[21]

            # search keyword
            self.driver.find_element_by_xpath('//*[@id="search.keyword.query"]').clear()
            self.driver.find_element_by_xpath('//*[@id="search.keyword.query"]').send_keys(search_keyword)
            self.driver.find_element_by_xpath('//*[@id="search.keyword.query"]').send_keys(Keys.ENTER)
            time.sleep(0.5)

            # 여기서 검색된 결과를 분기한다 1은 바로 결과값 가져오고 1+@ 는 원하는 값 찾는다.
            content_length = self.driver.find_elements_by_xpath('//*[@id="info.search.place.list"]/li/div[3]')
            if len(content_length) == 1:
                # a 는 dict
                crawled_data = self.get_data(len(content_length))
            '''else:
                for content in range(1, len(content_length) + 1):
                    target_address_road = self.driver.find_element_by_xpath('//*[@id="info.search.place.list"]/li[{content}]/div[5]/div[2]/p[1]'.format(content=content)).text
                    check = self.compare_with_address(address_location=address_location, address_road=address_road, address_target=target_address_road)
                    if check is True:
                        crawled_data = self.get_data(content)'''
            # 최종 출력할 결과물에 필요한 데이터만 추출하자.
            # 필요한 데이터는???
            # 가게이름
            row_data = {
                'id': row[0],
                'company': row[21],
                'address_location': address_location
            }
            row_data.update(crawled_data)
            res.append(row_data)
        return res

    def save(self, arr):
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        file_count = 1
        wb = Workbook()
        ws = wb.active
        # 첫행 입력
        ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
                   '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
                   '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드', '평점', '운영시간'))
        # DB 모든 데이터 엑셀로
        cnt = 0
        for row in arr:
            cnt += 1
            a = 'A2211_동물병원'
            b = row['company']
            c = row['company']
            d = row['address_road'] if row['address_road'] != '' else row['address_location']
            e = row['phone']
            f = date_now
            g = '0'
            h = '카카오지도'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            l = 'http'
            m = row['url']
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#동물병원'
            v = row['ranking']
            w = row['open_hour']
            insert = (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        wb.save('C:/workSpace/flask_crawling/originalDatas/동물병원.xlsx')


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
