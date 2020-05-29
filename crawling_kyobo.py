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
        self.url_a = 'http://www.kyobobook.co.kr/categoryRenewal/' \
                   'categoryMain.laf?pageNumber=1&perPage=50&mallGb=KOR&linkClass=1105&ejkGb=&sortColumn=near_date'
        self.url_p = 'http://www.kyobobook.co.kr/categoryRenewal/' \
                     'categoryMain.laf?pageNumber=1&perPage=50&mallGb=KOR&linkClass=1101&ejkGb=KOR&sortColumn=near_date'
        self.url_d = 'http://www.kyobobook.co.kr/product/detailViewKor.laf?mallGb=KOR&ejkGb=KOR&linkClass=1105&barcode={}'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        # keyword = ['반려동물']
        keyword = ['반려식물']
        for key in keyword:
            a = self.crawl(key)
            self.save(a, key)
        self.cm.close()
        self.driver.close()

    def crawl(self, key):
        res = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        # now_month = self.now.month
        # reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        if key == '반려동물':
            self.driver.get(self.url_a)
        else:
            self.driver.get(self.url_p)
        self.driver.maximize_window()
        time.sleep(0.5)
        length = self.driver.find_elements_by_xpath('//*[@id="eventPaging"]/div/ul/li')
        self.length = len(length)/2
        for page in range(1, int(self.length)+1):
            time.sleep(1)
            content_length = self.driver.find_elements_by_xpath('//*[@id="prd_list_type1"]/li/div/div[1]/div[2]/div[1]/a/strong')
            for content in range(1, len(content_length) + 1):
                arr = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[1]/a'.format(content=content*2-1)
                )
                book_url = href_tag[0].get_attribute('href')
                pattern_url = r'\'([0-9]{5,})\''
                url = re.findall(pattern_url, book_url)
                book_name = self.driver.find_element_by_xpath('//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[1]/a/strong'.format(content=content*2-1)).text
                book_ctn = self.driver.find_element_by_xpath('//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[4]/span'.format(content=content*2-1)).text
                book_author = self.driver.find_element_by_xpath('//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[2]/span[1]'.format(content=content*2-1)).text
                book_publisher = self.driver.find_element_by_xpath('//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[2]/span[2]'.format(content=content*2-1)).text
                book_date = self.driver.find_element_by_xpath('//*[@id="prd_list_type1"]/li[{content}]/div/div[1]/div[2]/div[2]/span[3]'.format(content=content*2-1)).text

                arr['book_url'] = url[0]
                arr['book_name'] = book_name
                print(book_name)
                arr['book_ctn'] = book_ctn
                arr['book_author'] = book_author
                arr['book_publisher'] = book_publisher
                arr['book_date'] = book_date.replace('.', '-')
                res.append(arr)

            if page != int(self.length):
                self.cnt += 1
                self.driver.execute_script("javascript:_go_targetPage('{}')".format(self.cnt))
        # save(res, key)
        return res

    def save(self, arr, key):
        keyset = {
            '반려동물 전문서적': 'A2354',
            '반려식물 전문서적': 'P2354'
        }
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        wb = Workbook()
        ws = wb.active
        # 첫행 입력
        ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
                   '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
                   '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드', '가변필드 메타명', '추가필드#1'))
        # DB 모든 데이터 엑셀로
        cnt = 0
        for row in arr:
            cnt += 1
            a = '{set}_{word}'.format(set=keyset['{} 전문서적'.format(key)], word=str(cnt).zfill(4))
            b = row['book_name']
            c = row['book_publisher']
            d = row['book_ctn']
            e = row['book_author']
            f = date_now
            g = '0'
            h = '교보문고'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = self.url_d.format(row['book_url'])
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#{key}, #책, #{key} 서적'.format(key=key)
            v = '@{fir}'.format(fir='출판일')
            w = row['book_date']
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u, v, w)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['{} 전문서적'.format(key)], word=key+' 전문서적'))
        

if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
