import math
import re

from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import os


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
        self.url = 'http://www.gumico.com/event/'
        self.url_dept1 = {
            1: 'exhibit_list.php',
            2: 'conven_list.php',
            3: 'event_list.php'
        }
        self.url_dept2 = 'page={page}&search_text=&search_gubun=B&search_type=year&s_date=&e_date=&search_year={year}&search_month='

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        crawl_results = self.crawl()  # 올해 행사일정 크롤링
        for res in crawl_results:
            print(res)
        # self.crawl_append(crawl_results)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#primary > div > div > div > div > div.v-contents')
            event_type = self.soup.select('#primary > div > div > div > div > header > p.type > span')
            row['page_source'] = str(self.page_source)
            row['event_type'] = event_type[0].text
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        for i in range(1, len(self.url_dept1)+1):
            self.driver.get(self.url+self.url_dept1[i])
            self.driver.maximize_window()

            # 올해의 시간을 구함.
            now_year = self.now.strftime('%Y')
            reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')

            # 올해 년도 검색
            self.driver.find_element_by_xpath('//*[@id="year"]').click()
            select = Select(self.driver.find_element_by_xpath('//*[@id="search_year"]'))
            select.select_by_visible_text(now_year+'년')
            self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/form/fieldset/button').click()

            # 페이지 길이 구하기.
            #if i != 2:
            #    temp_pages = self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/b').text
            #    pages = int(temp_pages)/10
            #    self.length = math.ceil(pages)
            #else:
            page_length = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[2]/a')
            self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/div[2]/a[{}]'.format(len(page_length))).click()
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.length = self.driver.find_element_by_xpath('//*[@id="PageWrap"]/div/div[2]/strong').text
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

            for page in range(1, int(self.length) + 1):
                print(page)
                self.driver.get(self.url.format(page=page, year=now_year))
                if i != 2:
                    length = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[1]/ul/li')
                else:
                    length = self.driver.find_elements_by_xpath('//*[@id="PageWrap"]/div/div[1]/table/tbody/tr')

                for content in range(1, len(length) + 1):
                    dic = {}
                    if i != 2:
                        href_tag = self.driver.find_elements_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/table/tbody/tr[{content}]/th/a'.format(content=content + 1)
                        )
                        temp_date = self.driver.find_element_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/ul/li[{content}]/dl/dd/ol/li[1]'.format(
                                content=content + 1)).text
                        pattern = r'\s([0-9]*-[0-9]*-[0-9]*)\s'
                        start_date = re.findall(pattern, temp_date)
                    else:
                        href_tag = self.driver.find_elements_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/ul/li[{content}]/dl/dt/a'.format(content=content + 1)
                        )
                        temp_date = self.driver.find_element_by_xpath(
                            '//*[@id="PageWrap"]/div/div[1]/table/tbody/tr[{content}]/td[1]'.format(
                                content=content + 1)).text
                        start_date = temp_date[0:temp_date.index('~')].strip()
                    event_page_url = href_tag[0].get_attribute('href')
                    event_name = href_tag[0].get_attribute('text')
                    self.event_type = self.driver.find_element_by_xpath(
                        '//*[@id="contents"]/h3'.format(content=content)).text

                    dic['convention_name'] = 'gumico'
                    dic['event_name'] = event_name
                    dic['event_type'] = self.event_type
                    dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                    dic['source_url'] = event_page_url
                    dic['home_page'] = 'http://www.gumico.com/main/main.php'
                    dic['reg_date'] = reg_date
                    compare.append(dic)
                    print(dic)
        print(compare)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()