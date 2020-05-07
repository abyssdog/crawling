from bs4 import BeautifulSoup as Bs
from selenium import webdriver
import datetime
import os
import pymysql

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
        self.url = 'http://www.bexco.co.kr/kor/EventSchedule/list.do?page={page}&mCode=MN0015&allChk=Y&mode=all_api_crawler&modeall=all_api_crawler&sch_event_gb=002&sch_micro_gb=&sch_count=1&sch_subject=&sch_start_date=&sch_end_date='
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

    def run_crawl(self):
        self.crawl()  # 올해 행사일정 크롤링

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
        #self.driver.find_element(By.XPATH, '//*[@id="dP1"]').clear()
        #self.driver.find_element(By.XPATH, '//*[@id="dP1"]').send_keys('2000-01-01')
        #self.driver.find_element(By.XPATH, '//*[@id="dP2"]').clear()
        #self.driver.find_element(By.XPATH, '//*[@id="dP2"]').send_keys('2020-02-00')
        #self.driver.find_element(By.XPATH, '//*[@id="searchForm"]/div[1]/a').click()

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for page in range(1, 540):
            self.driver.get(self.url.format(page=page))
            for content in range(1, 11):
                url = self.driver.find_elements_by_xpath('//*[@id="forPrint"]/div[1]/div/div[{content}]/div[2]/strong/a'.format(content=content))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_xpath('//*[@id="forPrint"]/div[1]/div/div[{content}]/div[2]/strong/a'.format(content=content)).click()

                contents = self.driver.find_elements_by_xpath('//*[@id="contents"]/div[2]/div[2]')
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#contents > div.cont > div.view_wrap')

                _dict['convention_name'] = 'bexco'
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
