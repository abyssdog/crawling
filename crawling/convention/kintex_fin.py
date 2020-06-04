from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import parse
from urllib.parse import quote
import datetime
import math
import os
import re
# import time
import urllib.request


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'kintex'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url_base = 'https://www.kintex.com'
        self.url = 'https://www.kintex.com/client/c010101/c010101_00.jsp'
        self.url_dept = '?sField=&sWord=&eventClCode=&prmtrNm=&' \
                        'koreanEventNm=&searchType=year&yearYear={year}&cPage={page}'

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
            self.page_source = self.soup.select('#content > div.schedule > div')
            row['page_source'] = str(self.page_source)
            event_content = self.soup.select('#content > div.schedule > div > div > dl:nth-child(11) > dd')
            if len(event_content) > 0:
                row['ctn'] = event_content[0].text
            else:
                row['ctn'] = ''
            temp_img_src = self.soup.select('#PageWrap > div > div.ViewInfo > p > img')
            ab = datetime.datetime.now()
            date_now = ab.strftime('%Y%m%d%H%M%S')
            file_name = date_now + str(ab.microsecond)
            if len(temp_img_src) > 0:
                temp_src = temp_img_src[0].attrs.get('src')
                encoding_url = parse.urlparse(temp_src[3:len(temp_src)])
                print(encoding_url)
                urllib.request.urlretrieve(
                    self.url_base + quote(encoding_url.path),
                    '../../originalDatas/' + file_name + '.png')
                img_src = file_name + '.png'
            else:
                img_src = ''
            row['img_src'] = img_src
            print(row['event_name'])
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
        self.driver.find_element_by_xpath('//*[@id="sidebar"]/ul/li[1]/a').click()
        self.driver.find_element_by_xpath('//*[@id="radio_period2"]').click()
        select = Select(self.driver.find_element_by_xpath(
            '//*[@id="content"]/div[2]/div[1]/form/div/div/dl[3]/dd/select'))
        select.select_by_visible_text(now_year)
        self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[1]/form/div/div/p/input').click()

        # 페이지 길이 구하기.
        first_page_size = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li/a')
        if len(first_page_size) == 4:
            self.length = 1
        else:
            temp_page_length = self.driver.find_elements_by_xpath(
                '//*[@id="content"]/div[2]/div[2]/ul/li[{}]/a'.format(len(first_page_size)-1))
            first_page_length = temp_page_length[0].get_attribute('text')
            if int(first_page_length) < 10:
                self.length = first_page_length
            else:
                self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[14]/a').click()
                max_length = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li')
                self.length = self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[{}]/strong'.format(len(max_length)-2)).text
                self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[1]/a').click()

        for page in range(1, int(self.length)+1):
            self.driver.get(self.url+self.url_dept.format(page=page, year=now_year))
            contents_size = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/fieldset/table/tbody/tr')
            for content in range(1, len(contents_size)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[2]/a'.format(content=content)
                )
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[3]'.format(
                        content=content)).text
                start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-')
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text').strip()
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[5]/img'.format(
                        content=content)).get_attribute('alt')

                dic['convention_name'] = 'kintex'
                dic['event_name'] = event_name
                print(event_name)
                dic['event_type'] = self.event_type.replace("[", "").replace("]", "")
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'https://www.kintex.com/'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
