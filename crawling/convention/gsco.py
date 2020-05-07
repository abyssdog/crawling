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
        self.url = 'http://www.gsco.kr/contents.htm?page={page}&vType=list&code=2_1'
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
        self.driver.get(self.url.format(page=1))
        self.driver.maximize_window()

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        # setting date
        #wait = WebDriverWait(self.driver, 10).until(
        #    EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/div[1]/div[1]/h2')))
        #self.driver.execute_script('document.getElementsByName("sdate")[0].removeAttribute("readonly")')
        #self.driver.execute_script('document.getElementsByName("edate")[0].removeAttribute("readonly")')
        #self.driver.find_element_by_xpath('//*[@id="sdate"]').clear()
        #self.driver.find_element_by_xpath('//*[@id="edate"]').clear()
        #self.driver.find_element_by_xpath('//*[@id="sdate"]').send_keys('2010-01-01')
        #self.driver.find_element_by_xpath('//*[@id="edate"]').send_keys('2020-01-30')
        #self.driver.find_element_by_xpath('//*[@id="listForm"]/fieldset/div[3]/input[2]').click()

        # go last page
        #WebDriverWait(self.driver, 10).until(
        #    EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[2]/div[3]/ul/li[14]/a')))
        #last = self.driver.find_elements_by_xpath('//*[@id="container"]/div[2]/form/div[3]/a')
        #self.driver.find_element_by_xpath('//*[@id="container"]/div[2]/form/div[3]/a[{last}]'.format(last=last)).click()

        # get page_length
        #page_length = self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[3]/ul/li/strong').text
        #pages = int(page_length)

        # go first page
        # self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[3]/ul/li[1]/a').click()

        #cnt = 3
        #for page in range(1, len(last)+1):
        for page in range(1, 37 + 1):
            #time.sleep(1)
            self.driver.get(self.url.format(page=page))
            #content_length = self.driver.find_elements_by_xpath('//*[@id="eventDiv"]/table/tbody/tr')
            content_length = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="eventDiv"]/table/tbody/tr')))
            for content in range(1, len(content_length)+1):
                #print('{page} 페이지 {content} 게시글 크롤링중'.format(page=page, content=content))
                url = self.driver.find_elements_by_xpath('//*[@id="eventDiv"]/table/tbody/tr[{content}]/td/a'.format(content=content))
                self.tempUrl = url[0].get_attribute('href')
                #WebDriverWait(self.driver, 10).until(
                #    EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[3]/a'.format(content=content))))
                self.driver.find_element_by_xpath('//*[@id="eventDiv"]/table/tbody/tr[{content}]/td/a'.format(content=content)).send_keys(Keys.ENTER)
                #self.driver.find_element_by_xpath(
                #    '//*[@id="content"]/div[2]/fieldset/table/tbody/tr[{content}]/td[3]/a'.format(content=content)).click()
                # content url 클릭
                # url_text = self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[{content}]/div/h2'.format(content=content)).text
                # self.driver.find_element_by_link_text(url_text).click()

                #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[2]/div')))

                #contents = self.driver.find_elements_by_xpath('//*[@id="eventView"]/table/tbody/tr/td')
                contents = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="eventView"]/table/tbody/tr/td')))
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#eventView > table > tbody > tr > td')

                #_dict['convention_name'] = 'gsco'
                _dict['contents'] = contents.text
                _dict['page_source'] = str(data)
                _dict['source_url'] = self.tempUrl
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date
                print(_dict)
                #self.content_insert(_dict)
                #self.driver.find_element_by_xpath('//*[@id="pop_detailSche"]/div[3]/a').click()
                self.driver.back()
                time.sleep(1)

            '''if cnt % 8 == 0:
                print('다음 페이지 이동')
                cnt = 3
                self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[8]/a').click()
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[1]/div[1]/h2')))
            else:
                cnt += 1
                print('{cnt} 페이지 이동'.format(cnt=page))
                self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div[2]/div[2]/ul/li[{cnt}]/a'.format(cnt=cnt)).click()
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[1]/div[1]/h2')))'''

        '''wait = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/a[13]')))
        self.driver.find_element_by_link_text("[마지막]").click()
        page_length = self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[9]/div/strong').text
        self.driver.find_element_by_link_text("[처음]").click()
        wait = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/strong')))
        # 1페이지 크롤링 시작
        cnt = 2
        for page in range(1, len(page_length)+1):
            content_length = self.driver.find_elements_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div/div/h2')
            for content in range(2, len(content_length)+2):
                time.sleep(1)
                #url = self.driver.find_elements_by_xpath('//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]/a[2]'.format(content=content))
                #self.tempUrl = url[0].get_attribute('href')
                wait = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="form"]/div/div/dl[1]/dt/label')))
                self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[{content}]/div/h2'.format(content=content)).click()
                # content url 클릭
                #url_text = self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[{content}]/div/h2'.format(content=content)).text
                #self.driver.find_element_by_link_text(url_text).click()

                wait = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="calender_data"]/div/table/tbody')))
                time.sleep(1)
                contents = self.driver.find_elements_by_xpath('//*[@id="calender_data"]/div/table/tbody')
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#calender_data > div > table > tbody')

                _dict['convention_name'] = 'hico'
                _dict['contents'] = contents[0].text
                _dict['page_source'] = str(data)
                _dict['source_url'] = 'None'
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date

                self.content_insert(_dict)
                self.driver.find_element_by_xpath('//*[@id="calender_data"]/a').click()
                time.sleep(1)
                self.driver.implicitly_wait(2)
                #self.driver.back()

            if cnt % 11 == 0:
                print('다음 페이지 이동')
                cnt = 2
                self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/a[12]').click()
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div/div/dl[1]/dt/label')))
            else:
                cnt += 1
                print('{cnt} 페이지 이동'.format(cnt=page))
                self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/a[{cnt}]'.format(cnt=cnt)).click()
                time.sleep(1)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="form"]/div/div/dl[1]/dt/label')))'''


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.crawl()
