# coding=utf-8
from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from urllib import parse
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import math
import os
import re
import time
import urllib.request


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'exco'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.base_url = 'https://www.exco.co.kr/'
        self.page_source = ''
        self.url = 'https://www.exco.co.kr/kor/program/schedule_year.html?gotoPage={page}&Ex_cate=&' \
                   'host=&event_name=&term=&search_word=&Start_year=&End_year=&Start_Month=&End_Month=' \
                   '&To_year1=&To_year2=&To_Month2=&startday='

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
            self.page_source = self.soup.select('#content > div.schview_con > ul.schview_txt')
            self.page_source += self.soup.select('#tab1')
            event_content = self.soup.select('#tab1')
            if len(event_content) > 0:
                row['ctn'] = event_content[0].text
            else:
                row['ctn'] = ''
            row['page_source'] = str(self.page_source)
            temp_event_type = self.soup.select('#content > div.t_schview > img')
            pattern = r'\_(\w*).gif'
            event_type_list = re.findall(pattern, temp_event_type[0].attrs.get('src'))
            if event_type_list[0] == 'conven':
                event_type = '컨벤션/회의'
            elif event_type_list[0] == 'event':
                event_type = '이벤트'
            elif event_type_list[0] == 'exhi':
                event_type = '전시회'
            else:
                event_type = '행사'
            row['event_type'] = event_type
            print(row['event_name'])

            img_source = self.soup.select('#content > div.schview_con > ul.schview_img > li.view_poster > img')
            ab = datetime.datetime.now()
            date_now = ab.strftime('%Y%m%d%H%M%S')
            file_name = date_now + str(ab.microsecond)
            if len(img_source) > 0:
                temp_src = img_source[0].attrs.get('src')
                if '/kor/images/common/noimg.gif' != temp_src:
                    encoding_url = parse.urlparse(temp_src)
                    # urllib.request.urlretrieve(self.base_url + quote(temp_src), '../../originalDatas/' + file_name + '.png')
                    urllib.request.urlretrieve(self.base_url + quote(encoding_url.path), '../../originalDatas/' + file_name + '.png')
                    img_src = file_name + '.png'
                else:
                    img_src = ''
            else:
                img_src = ''
            row['img_src'] = img_src

            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        self.driver.get(self.url.format(page=1))
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        # now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        # 페이지 길이 구하기.
        temp_pages = self.driver.find_element_by_xpath('//*[@id="content"]/p[3]/span').text
        pages = int(temp_pages)/10

        for page in range(1, math.ceil(pages)+1):
            self.driver.get(self.url.format(page=page))
            length = self.driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr/td[1]')
            for content in range(1, len(length)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="content"]/table/tbody/tr[{content}]/td[3]/a'.format(content=content+1)
                )
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text')
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/table/tbody/tr[{content}]/td[1]'.format(content=content+1)).text
                start_date = temp_date[0:temp_date.index('~')].strip()

                dic['convention_name'] = 'exco'
                dic['event_name'] = event_name
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'https://www.exco.co.kr/kor/index.html'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)
        print(compare)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
