import math

from bs4 import BeautifulSoup as Bs
from selenium.webdriver import ActionChains
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
        self.base_url = 'https://www.youtube.com/'
        self.url_a = 'https://www.youtube.com/results?search_query=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC&sp=CAMSAhAC'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        # keyword = ['반려동물']
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
        # now_month = self.now.strftime('%m')
        # now_month = self.now.month
        # reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        if key == '반려동물':
            self.driver.get(self.url_a)
        # else:
        #     self.driver.get(self.url_p)
        self.driver.maximize_window()
        time.sleep(0.5)
        while True:
            try:
                time.sleep(0.5)
                last = self.driver.find_element_by_xpath('//*[@id="contents"]/ytd-message-renderer').text
                if last == '결과가 더 이상 없습니다.':
                    break
            except NoSuchElementException:
                ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()

        length = self.driver.find_elements_by_xpath('//*[@id="contents"]/ytd-channel-renderer')
        for content in range(1, len(length)):
            youtube_name = self.driver.find_element_by_xpath('//*[@id="contents"]/ytd-channel-renderer[{content}]/div/div[2]/a/div[1]/ytd-channel-name/div/div/yt-formatted-string'.format(content=content)).text
            href_tag = self.driver.find_elements_by_xpath(
                '//*[@id="contents"]/ytd-channel-renderer[{content}]/div/div[2]/a'.format(
                    content=content))
            youtube_url = href_tag[0].get_attribute('href')
            print(youtube_name+''+youtube_url)
        return res

    def append(self, lis):
        for inlist in lis:
            self.driver.get(inlist['movie_url'])
            time.sleep(1)
            # html = self.driver.page_source
            # self.soup = Bs(html, 'html.parser')
            # page_source = self.soup.select('#kp-wp-tab-overview > div > div > div > div')
            # print(str(page_source[0]))
            # pattern_ctn = r'설명\<\/h2\>\<span\>(.*)\<\/span\>\<span\>'
            # pattern_date = r'개봉일\<\/a\>\s?\:\s?\<\/span\>\<span.*\"\>(.*)\(\<a'
            detail = self.driver.find_elements_by_xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div')
            pattern_ctn = r'설명\s?'
            pattern_date = r'개봉일\s?:\s?'
            pattern_producer = r'감독\s?:\s?'
            pattern_publisher = r'배급사\s?:\s?'
            pattern_make_company = r'제작사\s?:\s?'
            pattern_make_per = r'제작자\s?:\s?'

            for de in detail:
                ctn = re.search(pattern_ctn, de.text)
                dat = re.search(pattern_date, de.text)
                pro = re.search(pattern_producer, de.text)
                pub = re.search(pattern_publisher, de.text)
                mco = re.search(pattern_make_company, de.text)
                mpe = re.search(pattern_make_per, de.text)
                if ctn:
                    inlist['movie_ctn'] = de.text
                if dat:
                    inlist['movie_date'] = de.text
                if pro:
                    inlist['movie_producer'] = de.text
                if pub:
                    publish = de.text
                else:
                    publish = ''
                if mco:
                    make_company = de.text
                else:
                    make_company = ''
                if mpe:
                    make_person = de.text
                else:
                    make_person = ''
                gita = publish + make_company + make_person
                inlist['gita'] = gita
            # inlist['movie_ctn'] = self.driver.find_element_by_xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div[2]/div/div/div/div/span[1]').text
            # inlist['movie_date'] = self.driver.find_element_by_xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div[3]/div/div/span[2]').text
            # inlist['movie_producer'] = self.driver.find_element_by_xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div[4]/div/div/span[2]/a').text
            # try:
            #     inlist['movie_publisher'] = self.driver.find_element_by_xpath('//*[@id="kp-wp-tab-overview"]/div[1]/div/div/div/div[6]/div/div/span[2]/a').text
            # except NoSuchElementException:
            #     inlist['movie_publisher'] = ''
        return lis

    def save(self, arr, key):
        keyset = {
            '반려동물 영화 및 공연': 'A2385',
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
            a = '{set}_{word}'.format(set=keyset['{} 영화 및 공연'.format(key)], word=str(cnt).zfill(4))
            b = row['movie_name']
            c = row['movie_producer']
            d = row['movie_ctn']
            e = row['gita']
            f = date_now
            g = '0'
            h = '구글'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = self.url_a.format(row['movie_url'])
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#{key}, #영화, #{key} 영화 및 공연'.format(key=key)
            v = '@{fir}'.format(fir='개봉일')
            w = row['movie_date']
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u, v, w)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['{} 영화 및 공연'.format(key)], word=key+' 영화 및 공연'))
        

if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
