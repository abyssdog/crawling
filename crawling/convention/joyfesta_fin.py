from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.common.exceptions import ElementNotInteractableException
# from selenium.webdriver.common.by import By
import datetime
import os
# import math
# import re
import time


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'joyfesta'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'https://joyfesta.kr/Festival.festa'

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
            self.page_source = self.soup.select('#searchform > div.detailInfo > div.detailCont > table > tbody')
            self.page_source += self.soup.select('#detailBox01 > div > div.detNormal')
            self.page_source += self.soup.select('#detailBox01 > div > div.detIntroBox')
            ctn = self.soup.select('#detailBox01 > div > div.detIntroBox')
            row['ctn'] = ctn[0].text
            row['page_source'] = str(self.page_source)
            row['img_src'] = ''
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        # 올해 년도 검색
        # self.driver.find_element_by_xpath('//*[@id="sidebar"]/ul/li[1]/a').click()
        # self.driver.find_element_by_xpath('//*[@id="radio_period2"]').click()
        # select = Select(self.driver.find_element_by_xpath(
        #     '//*[@id="content"]/div[2]/div[1]/form/div/div/dl[3]/dd/select'))
        # select.select_by_visible_text(now_year)
        # self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/form/div/div/p/input').click()

        self.driver.execute_script("javascript:getFestivalList('36', true);")
        more_flag = True
        while more_flag:
            try:
                time.sleep(0.5)
                more = self.driver.find_element_by_xpath('//*[@id="wrap"]/section/div[4]/a')
                if more:
                    more.click()
            except ElementNotInteractableException:
                more_flag = False
                break

        # 페이지 길이 구하기.
        self.length = 1

        for page in range(1, self.length+1):
            contents_size = self.driver.find_elements_by_xpath('//*[@id="festivallist"]/li')
            for content in range(1, len(contents_size)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="festivallist"]/li[{content}]/div[2]/p[1]/a'.format(content=content)
                )
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="festivallist"]/li[{content}]/div[2]/div'.format(
                        content=content)).text
                start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-')
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text').strip()
                # self.event_type = self.driver.find_element_by_xpath(
                #     '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[5]/img'.format(
                #         content=content)).get_attribute('alt')

                dic['convention_name'] = 'joyfesta'
                dic['event_name'] = event_name
                dic['event_type'] = self.event_type.replace("[", "").replace("]", "")
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = ''
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
