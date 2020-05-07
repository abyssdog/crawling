from bs4 import BeautifulSoup as Bs
from selenium.webdriver.common.by import By
from selenium import webdriver
import datetime
import os
import pymysql

_dict = {}

class CrawlClass(object):
    species = 'catus'

    def get_ad(cls):
        print('aaa')

    def __init__(self):
        self.data = []
        self.host = 'localhost'
        self.port = 27017
        self.soup = ''
        self.tempUrl = ''
        self.url = 'http://www.at.or.kr/ac/event/acko311100/listList.action'
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

    def test123(cls):
        print('aaa')

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

    def crawl_atcenter(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.driver.find_element(By.XPATH, '//*[@id="dP1"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="dP1"]').send_keys('2020-01-01')
        self.driver.find_element(By.XPATH, '//*[@id="dP2"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="dP2"]').send_keys('2020-12-30')
        self.driver.find_element(By.XPATH, '//*[@id="searchForm"]/div[1]/a').click()

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for category in range(5, 12, 2):
            length = self.driver.find_elements_by_xpath(
                '//*[@id="printArea"]/div/div[{category}]/table/tbody/tr/th/a'.format(category=category))
            for tr in range(1, len(length)+1):
                url = self.driver.find_elements_by_xpath('//*[@id="printArea"]/div/div[{category}]/table/tbody/tr[{tr}]/th/a'.format(category=category, tr=tr))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_xpath('//*[@id="printArea"]/div/div[{category}]/table/tbody/tr[{tr}]/th/a'.format(category=category, tr=tr)).click()

                a = self.driver.find_elements_by_xpath('//*[@id="printArea"]/div/div[3]/table/tbody')

                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#printArea > div > div.board > table')

                _dict['convention_name'] = 'atCenter'
                _dict['contents'] = a[0].text
                _dict['page_source'] = str(data)
                _dict['source_url'] = self.tempUrl
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date

                self.content_insert(_dict)
                self.driver.back()


    def test(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        url = self.driver.find_elements_by_xpath('//*[@id="printArea"]/div/div[4]/table/tbody/tr[1]/th/a')
        self.tempUrl = url[0].get_attribute('href')
        self.driver.find_element_by_xpath('//*[@id="printArea"]/div/div[4]/table/tbody/tr[1]/th/a').click()

        html = self.driver.page_source
        self.soup = Bs(html, 'html.parser')
        data = self.soup.select('#printArea > div > div.board > table')
        print(data)
        # a = self.driver.find_elements_by_xpath('//*[@id="printArea"]/div/div[3]/table/tbody')

        #self.driver.back()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.crawl_atcenter()
