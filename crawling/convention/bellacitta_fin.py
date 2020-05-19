from bs4 import BeautifulSoup as Bs
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
        self.convention_name = 'whdtla0703'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'http://bellacitta.co.kr/html/sub/event.html'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        self.crawl()  # 올해 행사일정 크롤링
        #for row in crawl_results:
        #    self.cm.content_insert(row, 'original')
        self.cm.close()
        self.driver.close()

    def crawl(self):
        compare = []
        # 올해 년도 구하기
        # now_month = self.now.strftime('%m')
        now_month = self.now.month
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        self.driver.get(self.url)
        self.driver.maximize_window()

        for page in range(now_month, 12 + 1):
            time.sleep(1)
            self.driver.execute_script("tabOn('tab1',{page});".format(page=page))
            content_length = self.driver.find_elements_by_xpath('//*[@id="tab1c{}"]/table'.format(page))
            for content in range(1, len(content_length) + 1):
                dic = {}
                event_name = self.driver.find_element_by_xpath(
                    '//*[@id="tab1c{page}"]/table[{content}]/tbody/tr/td/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td/a'.format(page=page, content=content)
                ).text
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="tab1c{page}"]/table[{content}]/tbody/tr/td/table/tbody/tr[2]/td[2]/table/tbody/tr[2]/td[2]'.format(page=page, content=content)).text
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="tab1c{page}"]/table[{content}]/tbody/tr/td/table/tbody/tr[2]/td[2]/table/tbody/tr[4]/td[2]'.format(
                        page=page, content=content)).text
                if len(temp_date) > 0:
                    try:
                        start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-').replace(' ', '')
                    except ValueError:
                        start_date = temp_date[0:12].strip().replace('.', '-').replace(' ', '')
                else:
                    start_date = ''
                print(str(page) + ' ' + event_name)
                dic['convention_name'] = 'bellacitta'
                dic['event_name'] = event_name
                dic['event_type'] = self.event_type
                dic['event_start_date'] = start_date
                dic['source_url'] = ''
                dic['home_page'] = 'http://bellacitta.co.kr/html/index.html'
                dic['reg_date'] = reg_date

                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                self.page_source = self.soup.select('#tab1c{page} > table:nth-child({content}) > tbody > tr > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody'.format(page=page, content=2*content-1))
                dic['page_source'] = str(self.page_source)

                self.cm.content_insert(dic, 'original')
        # return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()

