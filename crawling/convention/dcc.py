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
        self.url = 'http://www.dcckorea.or.kr/'
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
        self.driver.get(self.url)
        self.driver.maximize_window()
        # iframes 로 전환해야지 xpath 사용할수 있음.
        time.sleep(1)
        iframe = self.driver.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(iframe)
        print('iframe 성공')
        time.sleep(1)
        frame = self.driver.find_element_by_tag_name('frame')
        self.driver.switch_to.frame(frame)
        print('frame 성공')
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="dcc-lnb"]/ul/li[1]/a').send_keys(Keys.ENTER)
        print('일정페이지 성공')
        #time.sleep(1)
        '''for i, iframe in enumerate(iframes):
            try:
                # iframe 안에 frame 이 하나 더 있어서 한번 더 전환
                self.driver.switch_to.frame(iframe)
                frames = self.driver.find_elements_by_tag_name('frame')
                for j, frame in enumerate(frames):
                    self.driver.switch_to.frame(frame)
                    # 여기다가 크롤링 소스 작성하면 됨.
                self.driver.switch_to.default_content()
            except:
                self.driver.switch_to.default_content()
                pass'''

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        cnt = 1
        first = 'f'
        for page in range(1, 280):
            length = self.driver.find_elements_by_xpath('//*[@id="notice_tb"]/tbody/tr')
            #time.sleep(1)
            for content in range(1, len(length)+1):
                #time.sleep(2)
                #page_wait = WebDriverWait(self.driver, 10).until(
                #    EC.presence_of_element_located((By.XPATH, '//*[@id="notice_tb"]/tbody/tr[{content}]/td[2]/a')))
                self.driver.find_element_by_xpath('//*[@id="notice_tb"]/tbody/tr[{content}]/td[2]/a'.format(content=content)).click()
                print('{a} 콘텐츠내용보기 성공'.format(a=content))
                content_wait = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="notice_tb"]/tbody')))
                #time.sleep(2)
                contents = self.driver.find_elements_by_xpath('//*[@id="notice_tb"]/tbody')
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#notice_tb > tbody')
                #time.sleep(2)
                _dict['convention_name'] = 'dcc'
                _dict['contents'] = contents[0].text
                _dict['page_source'] = str(data)
                _dict['source_url'] = 'None'
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date

                self.content_insert(_dict)
                #self.driver.back()
                self.driver.execute_script("window.history.go(-1)")
            time.sleep(1)
            if cnt % 10 == 0:
                if page % 10 == 0 and page > 10:
                    cnt = 1
                    self.driver.find_element_by_xpath('//*[@id="page_num"]/div/a[3]').click()
                    print('{cnt} 옆페이지 이동'.format(cnt=page))
                else:
                    cnt = 1
                    self.driver.find_element_by_xpath('//*[@id="page_num"]/div/a[1]').click()
                    time.sleep(1)
            else:
                cnt += 1
                print('{cnt} 페이지 이동'.format(cnt=page))
                self.driver.find_element_by_xpath('//*[@id="page_num"]/div/span[{cnt}]/a'.format(cnt=cnt)).click()
                time.sleep(1)



if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.crawl()
