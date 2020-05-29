import math

from bs4 import BeautifulSoup as Bs
from openpyxl import Workbook

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


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'pqi'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.cert_url = "javascript:detail('{value}');"
        self.page_source = ''
        # date format : 2020-00-00
        self.url = 'https://www.pqi.or.kr/inf/qul/infQulList.do'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keys = ['식물']
        for key in keys:
            crawl_results = self.crawl(key)
            result = self.crawl_append(crawl_results)
            self.save(result, key)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        count = 0
        for row in crawl_results:
            count += 1
            print(str(count) + ' : ' + row['cert_name'])
            self.driver.execute_script(row['source_url'])
            # self.driver.get(row['source_url'])
            time.sleep(0.5)
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#contents > section > article > article:nth-child(5) > div.text_square.blue_square')
            phone = self.soup.select('#contents > section > article > article.content_board > table > tbody > tr:nth-child(1) > td:nth-child(4) > div.orgNme > p')
            pattern_phone = r'(([0-9]{2,3}\-)?[0-9]{3,4}\-[0-9]{4})'
            cert_phone = re.findall(pattern_phone, phone[0].text)
            row['cert_phone'] = cert_phone[0][0]
            row['cert_ctn'] = self.page_source[0].text.replace('\t', '').strip()
            # self.cm.content_insert(row, 'original')
            self.driver.back()
        return crawl_results

    def crawl(self, key):
        compare = []
        # 올해 년도 구하기
        now_year = self.now.strftime('%Y')
        now_month = self.now.strftime('%m')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')
        month_last_day = calendar.monthrange(int(now_year), 12)

        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.find_element_by_xpath('//*[@id="searchQulNm"]').send_keys(key)
        self.driver.find_element_by_xpath('//*[@id="searchVO"]/article/article[1]/div[3]/button').click()

        # 페이지 길이 구하기
        target_text = self.driver.find_element_by_xpath('//*[@id="searchVO"]/article/article[2]/div[1]/p').text
        pattern_page_size = r'총 ([0-9]*)건'
        page_size = re.findall(pattern_page_size, target_text)
        self.length = math.ceil(int(page_size[0])/10)
        cnt = 0
        for page in range(1, self.length + 1):
            content_length = self.driver.find_elements_by_xpath('//*[@id="qulListTb"]/tbody/tr')

            for content in range(1, len(content_length) + 1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="qulListTb"]/tbody/tr[{content}]/td[3]/a'.format(content=content)
                )
                cert_href = href_tag[0].get_attribute('href')
                cert_name = href_tag[0].text
                # pattern_cert_href = r'\(\'([0-9]*)\'\)'
                # href = re.findall(pattern_cert_href, cert_href)
                cert_agent = self.driver.find_element_by_xpath('//*[@id="qulListTb"]/tbody/tr[{content}]/td[4]'.format(content=content)).text

                dic['cert_name'] = cert_name
                dic['cert_agent'] = cert_agent
                dic['cert_url'] = 'https://www.pqi.or.kr/inf/qul/infQulList.do'
                # dic['cert_ctn'] =  cert_ctn
                dic['source_url'] = cert_href
                compare.append(dic)

            if self.cnt != int(self.length):
                cnt += 1
                if page % 10 != 0:
                    self.cnt += 1
                    self.driver.execute_script("f_retrieveLinkPageList({page}); return false;".format(page=self.cnt))
                else:
                    cnt = 0
                    self.cnt += 1
                    self.driver.find_element_by_xpath('//*[@id="searchVO"]/article/article[2]/div[3]/ul/li[13]/a').click()
        return compare

    def save(self, arr, key):
        keyset = {
            '반려{} 전문자격'.format(key): 'A2353',
            '반려{} 전문자격'.format(key): 'P2353'
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
            print(str(cnt) + ' : ' + row['cert_name'])
            a = '{set}_{word}'.format(set=keyset['반려{} 전문자격'.format(key)], word=key)
            b = row['cert_name']
            c = row['cert_agent']
            d = row['cert_ctn']
            e = row['cert_phone']
            f = date_now
            g = '0'
            h = '민간자격정보서비스'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = row['cert_url']
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#반려{key} 전문자격, #반려{key}, #자격증, #교육'.format(key=key)
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u)
            ws.append(insert)
            print(insert)
            # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(set=keyset['반려{} 전문자격'.format(key)], word=key))


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
