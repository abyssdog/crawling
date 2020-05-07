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
        self.url = 'http://www.gumico.com/event/'
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
        self.tempLeng = 0
        self.url_dept = {
            1: 'exhibit_list.php',
            2: 'conven_list.php',
            3: 'event_list.php'
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
            charset='utf8mb4'
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
        detail_url = {
            1: 'http://www.gumico.com/event/exhibit_list.php?page={page}&search_text=&search_gubun=A&search_type=day&s_date=2020-01-01&e_date=2020-12-30&search_year=&search_month=',
            2: 'http://www.gumico.com/event/conven_list.php?page={page}&search_text=&search_gubun=B&search_type=day&s_date=2020-01-01&e_date=2020-12-30&search_year=&search_month=',
            3: 'http://www.gumico.com/event/event_list.php?page={page}&search_text=&search_gubun=C&search_type=day&s_date=2020-01-01&e_date=2020-12-30&search_year=&search_month='
        }
        for i in range(2, 4):
            url = self.url+self.url_dept[i]
            self.driver.get(url)
            self.driver.maximize_window()

            now = datetime.datetime.now()
            reg_date = now.strftime('%Y-%m-%d %H:%M:%S')

            # 검색 조건 세팅
            # self.driver.find_element_by_xpath('//*[@id="day"]')[0].click()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="PageWrap"]/div/form/fieldset/ul[1]/li[1]/label')))
            self.driver.execute_script('document.getElementsByName("s_date")[0].removeAttribute("readonly")')
            self.driver.execute_script('document.getElementsByName("e_date")[0].removeAttribute("readonly")')
            self.driver.find_element_by_xpath('//*[@id="day"]').click()
            self.driver.find_element_by_xpath('//*[@id="s_date"]').send_keys('2020-01-01')
            self.driver.find_element_by_xpath('//*[@id="e_date"]').send_keys('2020-12-30')
            self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/form/fieldset/button').click()

            # 페이지 맨끝 이동
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="PageWrap"]/div/form/fieldset/ul[1]/li[1]/label')))
            target = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[2]/a')
            self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/div[2]/a[{}]'.format(len(target)-2)).click()
            # 새창으로 이동
            if i == 1:
                self.driver.switch_to.window(self.driver.window_handles[1])
            lengthasd = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="PageWrap"]/div/div[2]/strong')))
            page_length = self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/div[2]/strong').text
            self.tempLeng = int(page_length)
            if i == 1:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            for page in range(1, self.tempLeng+1):
                if i != 2:
                    print("{page} 페이지 크롤링중".format(page=page))
                    self.driver.get(detail_url[i].format(page=page))
                    content_length = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[1]/ul/li')
                    for content in range(1, len(content_length)+1):
                        url = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[1]/ul/li[{content}]/dl/dt/a'.format(content=content))
                        self.tempUrl = url[0].get_attribute('href')
                        self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/div[1]/ul/li[{content}]/dl/dt/a'.format(content=content)).click()

                        contents = self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div').text
                        html = self.driver.page_source
                        self.soup = Bs(html, 'html.parser')
                        data = self.soup.select('#PageWrap > div')
                        #temp_data = []
                        #for x in data:
                        #    temp_data.append(str(x))
                        #tempText = b'data[0].text'.decode('utf-8')
                        #tempText.encoding = 'euc-kr'
                        #resText = tempText
                        _dict['convention_name'] = 'gumico'
                        _dict['contents'] = contents
                        #_dict['page_source'] = data[0].text
                        _dict['page_source'] = str(data)
                        _dict['source_url'] = self.tempUrl
                        _dict['home_page'] = self.url
                        _dict['reg_date'] = reg_date

                        self.content_insert(_dict)
                        self.driver.back()
                else:
                    print("{page} 페이지 크롤링중".format(page=page))
                    self.driver.get(detail_url[i].format(page=page))
                    content_length = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[1]/table/tbody/tr')
                    for content in range(1, len(content_length) + 1):
                        url = self.driver.find_elements_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/table/tbody/tr[{content}]/th/a'.format(content=content))
                        self.tempUrl = url[0].get_attribute('href')
                        self.driver.find_element_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/table/tbody/tr[{content}]/th/a'.format(content=content)).click()

                        contents = self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div').text
                        html = self.driver.page_source
                        self.soup = Bs(html, 'html.parser')
                        data = self.soup.select('#PageWrap > div')

                        _dict['convention_name'] = 'gumico'
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

