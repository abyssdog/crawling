from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
import datetime
import os
import re
import time


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'iccjeju'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'http://www.iccjeju.co.kr/Event/Schedule'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        self.crawl()  # 올해 행사일정 크롤링
        # self.crawl_append(crawl_results)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#content > div.schview_con > ul.schview_txt')
            self.page_source += self.soup.select('#tab1')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        # compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해 년도 구하기
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

        # 올해 년도 입력후 검색
        self.driver.find_element_by_xpath('//*[@id="sYear"]').send_keys(now_year)
        self.driver.find_element_by_xpath('//*[@id="sMonth"]').send_keys('01')
        self.driver.find_element_by_xpath('//*[@id="btn_search"]').click()
        first_page_size = self.driver.find_elements_by_xpath('//*[@id="pageLinkForm"]/a')
        if len(first_page_size) == 4:
            self.length = 1
        elif len(first_page_size) < 10:
            self.length = self.driver.find_element_by_xpath(
                '//*[@id="pageLinkForm"]/a[{}]'.format(len(first_page_size) - 2)).text
        else:
            self.driver.find_element_by_xpath('//*[@id="btn_last"]').click()
            self.length = self.driver.find_element_by_xpath('//*[@id="pageLinkForm"]/strong').text
            self.driver.find_element_by_xpath('//*[@id="btn_first"]').click()

        for page in range(1, int(self.length) + 1):
            contents = self.driver.find_elements_by_xpath(
                '//*[@id="sub_wrapper"]/div/div[2]/section/div[2]/div[3]/table/tbody/tr')
            for content in range(1, len(contents) + 1):
                print(content)
                self.page_source = ''
                dic = {}
                temp_event_name = self.driver.find_element_by_xpath(
                    '//*[@id="sub_wrapper"]/div/div[2]/section/div[2]/div[3]/table/'
                    'tbody/tr[{content}]/td[2]/div/ul/li[1]'.format(content=content)).text
                pattern_name = r'\:(.*)'
                event_name = re.findall(pattern_name, temp_event_name)
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="sub_wrapper"]/div/div[2]/section/div[2]/div[3]/table/tbody/'
                    'tr[{content}]/td[1]/span'.format(content=content)).text
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="sub_wrapper"]/div/div[2]/section/div[2]/div[3]/table/tbody/'
                    'tr[{content}]/td[2]/div/ul/li[2]'.format(content=content)).text
                pattern_date = r'\:\s?(([0-9]*)-([0-9]*)-([0-9]*))'
                start_date = re.findall(pattern_date, temp_date)

                dic['convention_name'] = 'iccjeju'
                dic['event_name'] = event_name[0]
                dic['event_type'] = self.event_type
                dic['event_start_date'] = datetime.datetime.strptime(start_date[0][0], '%Y-%m-%d').date()
                dic['source_url'] = ''
                dic['home_page'] = 'http://www.iccjeju.co.kr/'
                dic['reg_date'] = reg_date

                self.driver.find_element_by_xpath(
                    '//*[@id="sub_wrapper"]/div/div[2]/section/div[2]/div[3]/table/tbody/tr[{content}]/td[3]/a'.format(
                        content=content)).click()
                time.sleep(0.5)
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                self.page_source = self.soup.select('#pop_detailSche > div.sche-info > ul')
                self.page_source += self.soup.select('#pop_detailSche > div.sche-txt')
                dic['page_source'] = str(self.page_source)
                print(dic['event_name'])
                self.cm.content_insert(dic, 'original')

                self.driver.find_element_by_xpath('//*[@id="pop_detailSche"]/div[3]/a').click()

            if self.cnt != int(self.length):
                if page % 10 != 0:
                    now_page = self.driver.find_element_by_xpath('//*[@id="pageLinkForm"]/strong').text
                    if int(now_page) < 10:
                        self.driver.find_element_by_xpath(
                            '//*[@id="pageLinkForm"]/a[{}]'.format(int(now_page)+2)).click()
                    else:
                        self.driver.find_element_by_xpath(
                            '//*[@id="pageLinkForm"]/a[{}]'.format(int(now_page) - 10 + 2)).click()
                    self.cnt += 1
                else:
                    self.cnt += 1
                    self.driver.find_element_by_xpath('//*[@id="btn_next"]').click()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
