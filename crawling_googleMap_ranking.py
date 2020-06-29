import math

import pymysql
from bs4 import BeautifulSoup as Bs
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
        self.url = 'https://www.google.com/maps'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self, searchList):
        # keyword = self.get_search_list()
        a = self.crawl(searchList)
        self.cm.close()
        self.driver.close()

    def crawl(self, search_list):
        res = []
        self.driver.get(self.url)
        self.driver.maximize_window()
        # 0, 18, 19, 21
        for row in search_list:
            self.driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(row[21])
            self.driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(Keys.ENTER)
            check_flag = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div')
            if len(check_flag) > 2:
                listName = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/h3/span')
                listAddress = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/div[1]/div[2]/span[6]')
                #for addr in listAddress:
                #    if addr == searchAddress:
            else:
                address = self.driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]').text

                arr = {
                    'id': row[0],
                    'name': row[21],
                    'address_location': row[18],
                    'address_road': row[19],
                    'ranking': ''
                }
                res.append(arr)
        return res

    def get_search_list(self):
        conn = pymysql.connect(
            charset='utf8',
            db='convention',
            host='localhost',
            password='dangam1234',
            port=3306,
            user='root'
        )
        curs = conn.cursor()
        # business_condition_code = '01' => 정상영업
        sql = """SELECT location_address, road_name_address, company_name
  FROM animal_hospital
 WHERE business_condition_code = '01'
   AND location_x != '0.0'
   AND company_name LIKE '%에이블%'
'"""
        curs.execute(sql)
        sql_rows = curs.fetchall()
        conn.commit()
        conn.close()
        return sql_rows


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
    '''f = '바우뫼로'
    a = re.findall("([가-힣]*)", '서울특별시 서초구 바우뫼로 211 (양재동)')
    b = re.match("([가-힣]*)", '서울특별시 서초구 바우뫼로 211 (양재동)')
    c = re.search(f, '서울특별시 서초구 바우뫼로 211')
    if c:
        print(a[4])'''
