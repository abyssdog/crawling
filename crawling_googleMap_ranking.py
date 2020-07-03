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
        # a = self.crawl(searchList)
        a = self.crawl(searchList)
        self.cm.close()
        self.driver.close()
        return a

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
                   AND company_name LIKE '%에이블%'"""
        curs.execute(sql)
        sql_rows = curs.fetchall()
        conn.commit()
        conn.close()
        return sql_rows

    def compare_with_address(self, address_location, address_road, address_target):
        ar = address_road.split()
        al = address_location.split()
        at = address_target.split()
        cnt = 0
        for word in ar:
            if word in at:
                cnt += 1
        if len(ar) == cnt:
            return True
        else:
            for word in al:
                if word in at:
                    cnt += 1
            if len(al) == cnt:
                return True
            else:
                return False

    def crawl(self, search_list):
        res = []
        self.driver.get(self.url)
        self.driver.maximize_window()
        # 0 id, 18 address, 19 road address , 21 company name
        for row in search_list:
            dict_data = {}
            address_location = row[18]
            temp = row[19].split(',')
            address_road = temp[0]
            # input search keyword
            self.driver.find_element_by_xpath('//*[@id="searchboxinput"]').clear()
            self.driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(row[21])
            self.driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(Keys.ENTER)
            try:
                # 단일 개체 확인
                # a = self.driver.find_element_by_xpath(
                # '/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span')
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span')))
                address = self.driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]').text
                valid_flag = crawl.compare_with_address(address_location=address_location, address_road=address_road,
                                                        address_target=address)
                if valid_flag is False:
                    break
                ranking = self.driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span').text
                home_page = self.driver.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[10]/button/div/div[2]/div[1]').text
                # 영업일 div open
                self.driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div[1]/span[3]').click()
                time.sleep(1)
                open_days = self.driver.find_elements_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[12]/div[4]/table/tbody/tr/th/div[1]')
                open_hour = self.driver.find_elements_by_xpath(
                    '//*[@id="pane"]/div/div[1]/div/div/div[12]/div[4]/table/tbody/tr/td[1]/ul/li')
                dict_data = {
                    'ranking': ranking,
                    'homepage': home_page,
                    'day': open_days,
                    'hour': open_hour
                }

                print(address)
                print(valid_flag)
                res.append(dict_data)
            except Exception:
                pass
            # search result > 2
            '''searched_list = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div')
            if len(searched_list) > 2:
                listName = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/h3/span')
                listAddress = self.driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/div[1]/div[2]/span[6]')
                #for addr in listAddress:
                #    if addr == searchAddress:
            else:
                address_target = self.driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]').text
                #location = self.compare_with_address(address_base=address_location, address_target=address_target)
                #road = self.compare_with_address(address_base=address_road, address_target=address_target)
                #if road is True:
                #    print('aa')
                arr = {
                    'id': row[0],
                    'name': row[21],
                    'address_location': row[18],
                    'address_road': row[19],
                    'ranking': ''
                }
                res.append(arr)'''
        return res


if __name__ == '__main__':
    crawl = CrawlClass()
    # crawl.run_crawl()
    '''
    add_loca = '서울특별시 중구 을지로5가 133-1번지 뉴천지관광호텔'
    add_road = '서울특별시 중구 을지로38길 20, 뉴천지관광호텔 2층 (을지로5가)'
    option = webdriver.ChromeOptions()
    option.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=option)

    driver.get('https://www.google.com/maps')
    driver.maximize_window()

    driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys('헬릭스동물심장수술센터')
    driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(Keys.ENTER)
    # time.sleep(2)
    try:
        # 단일 개체 확인
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span')))
        ranking = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[2]/div/div[1]/span[1]/span/span').text
        address = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[8]/button/div/div[2]/div[1]').text
        valid_flag = crawl.compare_with_address(address_location=add_loca, address_road=add_road, address_target=address)
        home_page = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[10]/button/div/div[2]/div[1]').text
        # 영업일 div open
        driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div[1]/span[3]').click()
        time.sleep(1)
        open_days = driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div[4]/table/tbody/tr/th/div[1]')
        open_hour = driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[12]/div[4]/table/tbody/tr/td[1]/ul/li')

        print(address)
        print(valid_flag)
        temp_flag = 'one'
    except NoSuchElementException:
        # 리스트 확인
        # 딜레이 추가함. (랜더링 시간)
        temp_flag = 'list'
        event = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/h3/span')))
        rankings = driver.find_elements_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/span[3]/span[1]/span[1]/span')
        for t in event:
            print(t.text)
        for r in rankings:
            print(r.text)
        a = driver.find_elements_by_xpath('/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/div[2]/h3/span')
        searched_list = driver.find_elements_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div')
        listName = driver.find_elements_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div/div[1]/div[1]/div[1]/div[1]/div[2]/h3/span')
        listAddress = driver.find_elements_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]/div[1]/div/div[1]/div[2]/span[6]')
        pass
    print(temp_flag)'''
