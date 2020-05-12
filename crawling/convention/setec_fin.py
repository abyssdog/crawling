import re

from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import datetime
import os


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
        self.url = 'http://setec.or.kr/fus/bbs/selectBoardList.do' \
                   '?menuId=MNU_0000000000000053&bbsId=BBSMSTR_000000000032'
        self.url_dept = '&searchCnd=99&pageIndex={page}'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        crawl_results = self.crawl()  # 올해 행사일정 크롤링
        self.crawl_append(crawl_results)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#container > div > div.info_wrap > div.txt_area')
            self.page_source += self.soup.select('#container > div > div.detail')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        # 올해 년도 검색 - 검색결과가 제대로 반영안되서 의미 없음.
        '''self.driver.execute_script('document.getElementsByName("noticeStartDt")[0].removeAttribute("readonly")')
        self.driver.execute_script('document.getElementsByName("noticeEndDt")[0].removeAttribute("readonly")')
        self.driver.find_element_by_xpath('//*[@id="noticeStartDt"]').clear()
        self.driver.find_element_by_xpath('//*[@id="noticeStartDt"]').send_keys('{year}-01-01'.format(year=now_year))
        self.driver.find_element_by_xpath('//*[@id="noticeEndDt"]').clear()
        self.driver.find_element_by_xpath('//*[@id="noticeEndDt"]').send_keys('{year}-12-30'.format(year=now_year))
        self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/ul/li[1]/img[2]').click()
        self.driver.find_element_by_xpath('//*[@id="searchBtn"]').click()'''

        # 페이지 길이 구하기.
        first_page_size = self.driver.find_elements_by_xpath('//*[@id="container"]/div[2]/form/div[3]/a')
        self.length = len(first_page_size)

        '''self.driver.find_element_by_xpath(
            '//*[@id="container"]/div[2]/form/div[3]/a[{}]'.format(len(first_page_size))).click()
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/div[2]/form/div[2]/ul/li[1]')))
            self.length = len(first_page_size)
            self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[3]/a[1]').click()
        except TimeoutException:
            self.length = len(first_page_size) - 1
            self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[3]/a[1]').click()'''

        for page in range(1, self.length+1):
            self.driver.get(self.url+self.url_dept.format(page=page))
            content_length = self.driver.find_elements_by_xpath('//*[@id="container"]/div[2]/form/div[2]/ul/li')

            for content in range(1, len(content_length)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="container"]/div[2]/form/div[2]/ul/li[{content}]/a'.format(content=content)
                )
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="container"]/div[2]/form/div[2]/ul/li[{content}]/a/div[2]/ul/li[1]'.format(
                        content=content)).text
                pattern_date = r'\s(([0-9]*)-([0-9]*)-([0-9]*))'
                temp_date2 = re.findall(pattern_date, temp_date)
                start_date = temp_date2[0][0]
                # start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-')
                event_page_url = href_tag[0].get_attribute('href')
                event_name = self.driver.find_element_by_xpath(
                    '//*[@id="container"]/div[2]/form/div[2]/ul/li[{content}]/a/div[2]/strong'.format(content=content)).text
                self.event_type = '전시'

                dic['convention_name'] = 'setec'
                dic['event_name'] = event_name
                dic['event_type'] = self.event_type
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'http://setec.or.kr/'
                dic['reg_date'] = reg_date
                compare.append(dic)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
