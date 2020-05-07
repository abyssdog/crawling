import time
import re
import datefinder
from bs4 import BeautifulSoup as Bs
import datetime
from datetime import datetime
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
        self.host = '192.168.35.93'
        self.port = 27017
        self.soup = ''
        self.tempUrl = ''
        self.url_coex = 'http://www.coex.co.kr/event-performance/total-schedule-2/page/{page}'
        self.url_bexco = 'http://www.bexco.co.kr/kor/EventSchedule/main.do?mCode=MN0015&sch_event_gb=001'
        self.logId = ''
        self.maximum = 0
        self.page = 1
        '''self.dict = {
            'eventName': '',
            'place': '',
            'periodStart': '',
            'periodEnd': '',
            'timeStart': '',
            'timeEnd': '',
            'money': '',
            'homePage': '',
            'host': '',
            'management': '',
            'phoneNumber': '',
            'url': '',
            'htmlObject': ''
        }'''
        self.dict = {
            'convention_name': '',
            'contents': '',
            'home_page': '',
            'source_url': '',
            'reg_date': '',
            'page_source': ''
        }
        self.option = webdriver.ChromeOptions()
        #self.option.add_argument('headless')
        self.option.add_argument('window-size=1920x1080')
        #self.option.add_argument('disable-gpu')
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
        sql = """insert into convention
        (convention, event_name, place, period_start, time_start,
         money, home_page, host, management, phone_number, url, html_object) 
        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        sql_insert = curs.execute(sql,
                                  (_dict['convention'],
                                   _dict['eventName'],
                                   _dict['place'],
                                   _dict['periodStart'],
                                   _dict['timeStart'],
                                   _dict['money'],
                                   _dict['homePage'],
                                   _dict['host'],
                                   _dict['management'],
                                   _dict['phoneNumber'],
                                   _dict['url'],
                                   _dict['htmlObject']
                                   ))
        conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
        # res = curs.fetchall()
        print('commit success :', sql)
        conn.close()
        # val = res[0][0]+1  # 최신 채번을 위해서 +1
        # self.logId = val

    def coex_last_page(self):
        self.driver.find_element_by_xpath('//*[@id="calendar-start"]').clear()
        self.driver.find_element_by_xpath('//*[@id="calendar-start"]').send_keys("2010-01-01")
        #self.driver.find_element_by_xpath('//*[@id="calendar-start"]').send_keys(Keys.ENTER)
        self.driver.find_element_by_xpath('//*[@id="calendar-end"]').clear()
        self.driver.find_element_by_xpath('//*[@id="calendar-end"]').send_keys("2010-12-30")
        #self.driver.find_element_by_xpath('//*[@id="calendar-end"]').send_keys(Keys.ENTER)
        self.driver.find_element_by_xpath('//*[@id="search"]').send_keys(Keys.ENTER)

    def coex_page_length(self, url):
        length = 0
        self.driver.get(url.format(page=1))
        self.driver.find_element_by_xpath('//*[@id="calendar-start"]').clear()
        self.driver.find_element_by_xpath('//*[@id="calendar-start"]').send_keys("2010-01-01")
        self.driver.find_element_by_xpath('//*[@id="calendar-end"]').clear()
        self.driver.find_element_by_xpath('//*[@id="calendar-end"]').send_keys("2020-01-30")
        #time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="search"]').click()
        # self.driver.find_element_by_css_selector('#search').click()
        #time.sleep(1)
        #self.coex_last_page()
        # pagination = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a')
        last = self.driver.find_elements_by_xpath("//*[contains(text(), '마지막페이지')]/..")
        if len(last) > 0:
            self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a[11]').click()
            length = self.driver.find_element_by_xpath('//*[@class="current"]').text
        else:
            # last 가 없으면 10 이하임. => len(a.list)-1 를 먼저 구해서 여기다가 넣으면 될듯?
            print('test')
        # self.maximum = len(pagination)

        #response = requests.get(self.url.format(page=1))
        #source = response.text
        #soup = BeautifulSoup(source, 'html.parser')
        #print(soup)
        '''while 1:
            page_list = soup.findAll("div", {"class": "wp-pagenavi"})
            if not page_list:
                self.maximum = self.page - 1
                break
            self.page = self.page + 1'''
        print("총 " + str(length) + " 개의 페이지가 확인 됬습니다.")
        return length

    #http: // www.coex.co.kr / event - performance / total - schedule - 2 / page / 15?type = visitor & sv & period = month & search_sdate = 2010 - 01 - 31 & search_edate = 2010 - 12 - 15
    #http: // www.coex.co.kr / event - performance / total - schedule - 2 / page / 6?type = visitor & sv & period = month & search_sdate = 2010 - 01 - 31 & search_edate = 2010 - 12 - 15
    # a = self.driver.find_element_by_css_selector('#primary > div > div > div > div > dl > dd > ul > li:nth-child({}) > div > ul > li:nth-child(2) > a'.format(j)).get_attribute('href')
    def crawl_coex(self):
        _crawl = CrawlClass()
        maximum = _crawl.coex_page_length(self.url_coex)
        for i in range(1, maximum):
            self.driver.get(self.url_coex.format(page=i))
            for j in range(1, 11):
                url = self.driver.find_elements_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{}]/div/ul/li[2]/a'.format(j))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_css_selector('#primary > div > div > div > div > dl > dd > ul > li:nth-child({}) > div > ul > li:nth-child(2) > a'.format(j)).click()
                # find_elements_by_xpath 로 하면 list 로 리턴하고 거기서 text 로 해당 경로의 text 값 가져올수 있음.
                # "//*[contains(text(), '주최')]/.." => html 내용중 주최를 포함한 노드 리턴 /.. 는 해당 노드의 부모 노드 가져옴
                _dict['eventName'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '행사명(국문)')]/..")[0].text.split(' : ')[1]
                _dict['periodStart'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '개최기간')]/..")[0].text.split(' : ')[1]
                _dict['timeStart'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '관람시간')]/..")[0].text.split(' : ')[1]
                _dict['place'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '개최장소')]/..")[0].text.split(' : ')[1].split(' 지도보기')[0]
                _dict['homePage'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '관련웹사이트 ')]/..")[0].text.split(' : ')[1]
                _dict['host'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '주최')]/..")[2].text.split('\n')[1]
                _dict['management'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '주관')]/..")[0].text.split('\n')[1]
                _dict['money'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '입장료')]/..")[0].text.split('\n')[1]
                _dict['phoneNumber'] = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '전화번호')]/..")[0].text.split('\n')[1]
                _dict['url'] = self.tempUrl
                _dict['htmlObject'] = self.driver.page_source
                _dict['convention'] = 'coex'
                # _crawl.content_insert(_ditc)
                self.driver.back()
                time.sleep(2)
            d = self.driver.find_elements(By.XPATH, '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[1]/div/ul/li[4]')
            print(d)
        #pagination = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a')
        #self.maximum = len(pagination)
        #b = self.driver.find_elements_by_css_selector(
        #    '#primary > div > div > div > div > dl > dd > ul > li:nth-child > div > ul > li:nth-child(2) > a'
        #)
        '''for schedule in schedule_list:
            schedule.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[1]/div/ul/li[2]/a')
            self.dict['eventName'] = schedule.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[1]/div/ul/li[2]/a')'''
        '''html = driver.page_source
        self.soup = Bs(html, 'html.parser')
        data = self.soup.select(
            '// *[ @ id = "primary"] / div / div / div / div /dl/dd/div'
        )
        crawl.insert(data, self.soup)'''

    def test(self):
        tempUrl = 'http://www.coex.co.kr/event-performance/total-schedule-2/page/{page}?type=visitor&sv&period=month&search_sdate=2011-01-01&search_edate=2019-12-30'
        maximum = self.coex_page_length(tempUrl)
        for i in range(1, int(maximum)+1):
            # for i in range(37, 38):
            self.driver.get(tempUrl.format(page=i))
            time.sleep(2)
            postLength = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/ul/li')
            for j in range(1, len(postLength)+1):
                # for j in range(2, 3):
                print('{page}-페이지 {con}-게시글 크롤링중'.format(page=i, con=j))
                url = self.driver.find_elements_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{}]/div/ul/li[2]/a'.format(j))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_css_selector(
                    '#primary > div > div > div > div > dl > dd > ul > li:nth-child({}) > div > ul > li:nth-child(2) > a'.format(
                        j)).click()
                flag = self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/header/p[1]/span').text
                if flag == '지난공연':
                    break
                temp_event = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '행사명(국문)')]/..")[0].text.split(' : ')
                temp_period = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '개최기간')]/..")[0].text.split(' : ')
                temp_time = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '관람시간')]/..")[0].text.split(' : ')
                temp_place = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '개최장소')]/..")[0].text.split(' : ')
                temp_homePage = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '관련웹사이트 ')]/..")[0].text.split(' : ')

                temp_host = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '주최')]/..")
                temp_host_res = ''
                for th in temp_host:
                    if th.tag_name == 'li':
                        if th.text.find("\n") != -1:
                            temp_host_res = th.text
                            break
                temp_manage = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '주관')]/..")
                temp_manage_res = ''
                for tm in temp_manage:
                    if tm.tag_name == 'li':
                        if tm.text.find("\n") != -1:
                            temp_manage_res = tm.text
                            break
                temp_money = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '입장료')]/..")
                temp_phone = self.driver.find_elements_by_xpath(
                    "//*[contains(text(), '전화번호')]/..")

                '''if len(temp_host) > 3:
                    if len(temp_host) > 4:
                        flag_value = 4
                    else:
                        flag_value = 3
                else:
                    flag_value = 2
                if len(temp_manage) > 1:
                    if len(temp_manage) > 2:
                        flag_manage = 2
                    else:
                        flag_manage = 1
                else:
                    flag_manage = 0'''
                # print(temp_host_res)
                # host = temp_host[flag_value].text.split('\n')[1] if len(temp_host) != 0 else ''
                if temp_host_res != '':
                    host = temp_host_res.split('\n')[1] if len(temp_host) != 0 else ''
                else:
                    host = ''
                if temp_manage_res != '':
                    management = temp_manage_res.split('\n')[1] if len(temp_manage) != 0 else ''
                else:
                    management = ''
                money = temp_money[0].text.split('\n')[1] if len(temp_money) != 0 else ''
                phoneNumber = temp_phone[0].text.split('\n')[1] if len(temp_phone) != 0 else ''

                _dict['eventName'] = temp_event[1] if len(temp_event) > 1 else ''
                _dict['periodStart'] = temp_period[1] if len(temp_period) > 1 else ''
                _dict['timeStart'] = temp_time[1] if len(temp_time) > 1 else ''
                _dict['place'] = temp_place[1].split(' 지도보기')[0] if len(temp_place) > 1 else ''
                _dict['homePage'] = temp_homePage[1] if len(temp_homePage) > 1 else ''

                '''_dict['host'] = host[1] if len(host) > 1 else ''
                _dict['management'] = management[1] if len(management) > 1 else ''
                _dict['money'] = money[1] if len(money) > 1 else ''
                _dict['phoneNumber'] = phoneNumber[1] if len(phoneNumber) > 1 else '''''
                _dict['host'] = host
                _dict['management'] = management
                _dict['money'] = money
                _dict['phoneNumber'] = phoneNumber

                _dict['url'] = self.tempUrl
                _dict['htmlObject'] = self.driver.page_source
                _dict['convention'] = 'coex'
                self.content_insert(_dict)
                self.driver.back()
                time.sleep(1)

    def test_insert(self, _dict):
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

    def crawl_test(self):
        tempUrl = 'http://www.coex.co.kr/event-performance/total-schedule-2/page/{page}?type=visitor&sv&period=month&search_sdate=2011-01-01&search_edate=2020-01-30'
        maximum = self.coex_page_length(tempUrl)
        self.driver.maximize_window()

        now = datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(18, int(maximum) + 1):
            # for i in range(37, 38):
            self.driver.get(tempUrl.format(page=i))
            time.sleep(2)
            postLength = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/ul/li')
            for j in range(1, len(postLength) + 1):
                # for j in range(2, 3):
                print('{page}-페이지 {con}-게시글 크롤링중'.format(page=i, con=j))
                url = self.driver.find_elements_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{}]/div/ul/li[2]/a'.format(j))
                self.tempUrl = url[0].get_attribute('href')
                self.driver.find_element_by_css_selector(
                    '#primary > div > div > div > div > dl > dd > ul > li:nth-child({}) > div > ul > li:nth-child(2) > a'.format(
                        j)).click()

                contents = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div')
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                data = self.soup.select('#primary > div > div > div > div')

                _dict['convention_name'] = 'coex'
                _dict['contents'] = contents[0].text
                _dict['page_source'] = str(data)
                _dict['source_url'] = self.tempUrl
                _dict['home_page'] = self.url_coex
                _dict['reg_date'] = reg_date

                self.test_insert(_dict)
                self.driver.back()


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.test_insert1()
    # crawl.get_page_length()
    # crawl.crawl_coex()
    # crawl.crawl_bexco()
    #crawl.get_page_length()