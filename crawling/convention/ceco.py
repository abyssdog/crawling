from bs4 import BeautifulSoup as Bs
from selenium import webdriver
import datetime
import os
import pymysql

_dict = {}


class CrawlClass(object):
    def __init__(self):
        self.data = []
        self.host = 'localhost'
        self.port = 27017
        self.soup = ''
        self.tempUrl = ''
        self.url = 'https://www.ceco.co.kr/bbx/board.php?bx_table=01_01&sfl=wr_subject&sop=and&sdate=2020-01-01&edate=2020-12-31&page={page}'
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
        for page in range(1, 7):
            self.driver.get(self.url.format(page=page))
            length = self.driver.find_elements_by_xpath('//*[@id="gall_ul"]/li')
            for content in range(1, len(length)):
                url = self.driver.find_elements_by_xpath('//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]/a[2]'.format(content=content))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_xpath('//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]/a[2]'.format(content=content)).click()

                contents = self.driver.find_elements_by_xpath('//*[@id="bo_v_con"]')
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#bo_v_con')

                _dict['convention_name'] = 'ceco'
                _dict['contents'] = contents[0].text
                _dict['page_source'] = str(data)
                _dict['source_url'] = self.tempUrl
                _dict['home_page'] = self.url
                _dict['reg_date'] = reg_date

                self.content_insert(_dict)
                self.driver.back()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.crawl()
