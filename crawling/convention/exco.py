import time
import re
import datefinder
from bs4 import BeautifulSoup as Bs
import datetime
from selenium import webdriver
import inspect
import os
import pymongo
import pymysql
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


'''
 여기는 MariaDb 에다가 데이터 넣을거 테스트할 부분
'''
_dict = {}

class CrawlClass(object):
    def __init__(self):
        self.data = []
        self.host = 'localhost'
        self.port = 27017
        self.soup = ''
        self.tempUrl = ''
        self.url = 'https://www.exco.co.kr/kor/program/schedule.html?gotoPage={page}&Ex_cate=&host=&event_name=&term=2&search_word=&Start_year=&End_year=&Start_Month=&End_Month=&To_year1=2020&To_year2=&To_Month2=&startday='
        self.maximum = 0
        self.page = 1
        self.dict = {
            'convention_name': '',
            'contents': '',
            'home_page': '',
            'source_url': '',
            'reg_date': '',
            'page_source': ''
        }

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def content_insert(self, _dict):
        conn = pymysql.connect(
            host=self.host,
            port=3306,
            user='root',
            password='dangam1234',
            db='convention',
            charset='utf8'
        )
        curs = conn.cursor()
        sql = """insert into raw_schedule
        (convention_name, page_source, contents, source_url, home_page, reg_date) 
        values(%s, %s, %s, %s, %s, %s)"""
        sql_insert = curs.execute(sql,
                                  (_dict['convention_name'],
                                   _dict['page_source'],
                                   _dict['contents'],
                                   _dict['source_url'],
                                   _dict['home_page'],
                                   _dict['reg_date']
                                   ))
        conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
        print('commit success :', sql)
        conn.close()

    def crawl(self):
        self.driver.get(self.url.format(page=1))
        self.driver.maximize_window()

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for page in range(1, 27):
            self.driver.get(self.url.format(page=page))
            length = self.driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr')
            for content in range(2, len(length)+1):
                url = self.driver.find_elements_by_xpath('//*[@id="content"]/table/tbody/tr[{content}]/td[2]/a'.format(content=content))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr[{content}]/td[2]/a'.format(content=content)).click()

                contents = self.driver.find_element_by_xpath('//*[@id="content"]').text
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#content')

                _dict['convention_name'] = 'exco'
                _dict['contents'] = contents
                _dict['page_source'] = str(data)
                _dict['source_url'] = self.tempUrl
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date

                self.content_insert(_dict)
                self.driver.back()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.crawl()
