import time

from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
# from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import datetime
import os
# import math
import re


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'dcc'
        self.cnt = 1
        self.flag = True
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'http://www.dcckorea.or.kr/'

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
            # self.driver.get(row['source_url'])
            self.driver.execute_script("javascript:goView({});".format(row['source_url']))
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#notice_tb > tbody')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()
        iframe = self.driver.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(iframe)
        frame = self.driver.find_element_by_tag_name('frame')
        self.driver.switch_to.frame(frame)
        # WebDriverWait(self.driver, 5).until(
        #    EC.element_to_be_clickable((By.XPATH, '//*[@id="dcc-lnb"]/ul/li[1]/a')))
        self.driver.find_element_by_xpath('//*[@id="dcc-lnb"]/ul/li[1]/a').click()
        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')
        cnt = 0
        first_page_size = self.driver.find_elements_by_xpath('//*[@id="page_num"]/div/span')
        for page in range(1, len(first_page_size)):
            length = self.driver.find_elements_by_xpath('//*[@id="notice_tb"]/tbody/tr')
            if not self.flag:
                break
            for content in range(1, len(length)+1):
                time.sleep(0.5)
                dic = {}
                temp_event_date = self.driver.find_element_by_xpath('//*[@id="notice_tb"]/tbody/tr[{content}]/td[3]'.format(content=content)).text
                temp_start_date = temp_event_date[0:temp_event_date.index('~')].strip().replace('/', '-')
                start_date = datetime.datetime.strptime(temp_start_date, '%Y-%m-%d').date()
                current_year = datetime.datetime.strptime('{}-01-01'.format(now_year), '%Y-%m-%d').date()
                if start_date > current_year:
                    href_tag = self.driver.find_elements_by_xpath(
                        '//*[@id="notice_tb"]/tbody/tr[{content}]/td[2]/a'.format(content=content)
                    )
                    event_page_url = href_tag[0].get_attribute('href')
                    event_name = href_tag[0].get_attribute('text')
                    pattern_url_value = r'\([0-9]*\)'
                    url_value = re.findall(pattern_url_value, event_page_url)
                    print(str(start_date) + ' ' + event_name)

                    dic['convention_name'] = 'dcc'
                    dic['event_name'] = event_name
                    dic['event_type'] = '행사'
                    dic['event_start_date'] = start_date
                    dic['source_url'] = url_value[0].replace('(', '').replace(')', '')
                    dic['home_page'] = 'http://www.dcckorea.or.kr/'
                    dic['reg_date'] = reg_date
                    dic['crawl_version'] = crawl_date
                    compare.append(dic)
                else:
                    self.flag = False
                    break
            if self.cnt != len(first_page_size):
                if page % 10 != 0:
                    cnt += 1
                    # self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/a[1]').send_keys(Keys.ENTER)
                    self.driver.find_element_by_xpath(
                        '//*[@id="page_num"]/div/span[{page}]/a'.format(page=cnt)).click()
                    self.cnt += 1
                else:
                    cnt = 0
                    self.cnt += 1
                    next_index = self.driver.find_elements_by_xpath('//*[@id="page_num"]/div/a')
                    self.driver.find_element_by_xpath('//*[@id="page_num"]/div/a[]'.format(len(next_index)-1)).click()
        print(compare)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
