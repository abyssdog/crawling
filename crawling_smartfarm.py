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
        self.url = 'https://www.smartfarmkorea.net/company/list.do'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        key = '반려식물'
        a = self.crawl()
        b = self.append(a)
        self.save(b, key)
        self.cm.close()
        self.driver.close()

    def crawl(self):
        res = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        # now_month = self.now.month
        # reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[3]/div[1]/ul/li[2]/a').click()
        time.sleep(0.5)

        length = self.driver.find_element_by_xpath('//*[@id="searchFrm"]/div/p/span').text
        self.length = math.ceil(int(length)/10)

        for page in range(1, self.length+1):
            content_length = self.driver.find_elements_by_xpath('//*[@id="contWrap"]/div/div[3]/div[3]/table/tbody/tr/td[3]/a')

            for content in range(1, len(content_length) + 1):
                arr = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="contWrap"]/div/div[3]/div[3]/table/tbody/tr[{content}]/td[3]/a'.format(content=content+1)
                )
                company_url = href_tag[0].get_attribute('onclick')
                company_name = href_tag[0].text
                company_phone = self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[3]/div[3]/table/tbody/tr[{content}]/td[5]'.format(content=content+1)).text

                arr['company_url'] = company_url
                arr['company_name'] = company_name
                arr['company_phone'] = company_phone
                res.append(arr)

            if page != int(self.length):
                self.cnt += 1
                self.driver.execute_script("setPageNum({});return false; ".format(self.cnt))
        # save(res, key)
        return res

    def append(self, lis):
        for inlist in lis:
            self.driver.execute_script(inlist['company_url'])
            time.sleep(0.5)
            inlist['company_product'] = self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[4]/div[1]/table/tbody/tr[5]/td[2]').text
            inlist['company_home'] = self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[4]/div[1]/table/tbody/tr[9]/td[1]').text
            inlist['company_email'] = self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[4]/div[1]/table/tbody/tr[9]/td[2]').text
            inlist['company_address'] = self.driver.find_element_by_xpath('//*[@id="contWrap"]/div/div[4]/div[1]/table/tbody/tr[7]/td').text
            self.driver.back()
        return lis

    def save(self, arr, key):
        keyset = {
            '반려식물 기술융합': 'P2113'
        }
        now = datetime.datetime.now()
        date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
        wb = Workbook()
        ws = wb.active
        # 첫행 입력
        ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
                   '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
                   '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드', '가변필드 메타명', '추가필드#1', '추가필드#2', '추가필드#3'))
        # DB 모든 데이터 엑셀로
        cnt = 0
        for row in arr:
            cnt += 1
            a = '{set}_{word}'.format(set=keyset['{} 기술융합'.format(key)], word=str(cnt).zfill(4))
            b = row['company_name']
            c = row['company_name']
            d = row['company_product']
            e = row['company_phone']
            f = date_now
            g = '0'
            h = '스마트팜코리아 홈페이지'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = 'https://www.smartfarmkorea.net/company/list.do'
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#{key} 기술융합, #기술, #{key}'.format(key=key)
            v = '@{fir}, @{sec}, @{thi}'.format(fir='출판일', sec='홈페이지', thi='주소')
            w = row['company_email']
            x = row['company_home']
            y = row['company_address']
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u, v, w, x, y)
            ws.append(insert)
            print(insert)
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['{} 기술융합'.format(key)], word=key+' 기술융합'))
        

if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
