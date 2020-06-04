from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib import parse
from urllib.parse import quote
import datetime
import math
import os
import re
import time
import urllib.request

class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'hico'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_name = ''
        self.event_type = ''
        self.event_date = ''
        self.page_source = ''
        self.url_base = 'http://www.crowncity.kr'
        self.url = 'http://www.crowncity.kr/hico/ko/event/calender_list.do'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        self.crawl()  # 올해 행사일정 크롤링
        #self.crawl_append(crawl_results)
        self.cm.close()
        self.driver.close()

    '''def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#content > div.schedule > div')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')'''

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        # 올해 년도 검색
        self.driver.find_element_by_xpath('//*[@id="searchStartDate"]').clear()
        self.driver.find_element_by_xpath('//*[@id="searchStartDate"]').send_keys('{}-01-01'.format(now_year))
        self.driver.find_element_by_xpath('//*[@id="searchEndDate"]').clear()
        self.driver.find_element_by_xpath('//*[@id="searchEndDate"]').send_keys('{}-12-30'.format(now_year))
        self.driver.find_element_by_xpath('//*[@id="form"]/div/div/button').click()

        # 페이지 길이 구하기.
        # hico는 일정들과 페이지네이션이 같은 div를 쓰기때문에 일단 row 갯수부터 구한다.
        first_page_rows = self.driver.find_elements_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div')
        first_page_size = self.driver.find_elements_by_xpath(
            '//*[@id="sub_content"]/div[1]/div[1]/div[{}]/div/a'.format(len(first_page_rows)))
        last_page_text = self.driver.find_element_by_xpath(
            '//*[@id="sub_content"]/div[1]/div[1]/div[{row}]/div/a[{size}]'.format(
                row=len(first_page_rows), size=len(first_page_size))).get_attribute('onclick')
        pattern = r'fnLinkPage\((.*)\)'
        last_page = re.findall(pattern, last_page_text)
        self.length = last_page[0]

        for page in range(1, int(self.length)+1):
            page_rows = self.driver.find_elements_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div')
            contents_size = self.driver.find_elements_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div/div/h2')
            for content in range(1, len(contents_size) + 1):
                time.sleep(0.5)
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="sub_content"]/div[1]/div[1]/div[{content}]/div/h2'.format(content=content+1)
                )
                self.event_name = href_tag[0].text
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="sub_content"]/div[1]/div[1]/div[{content}]/div/p[1]'.format(
                        content=content+1)).text
                self.event_date = temp_date[0:temp_date.index('~')].strip()

                dic['convention_name'] = 'hico'
                dic['event_name'] = self.event_name
                dic['event_type'] = '행사'
                dic['event_start_date'] = datetime.datetime.strptime(self.event_date, '%Y-%m-%d').date()
                dic['source_url'] = 'http://www.crowncity.kr/hico/ko/event/calender_list.do'
                dic['home_page'] = 'http://www.crowncity.kr/hico/ko/main/main.do'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                dic['ctn'] = ''

                a = href_tag[0].get_attribute('onclick')
                self.driver.execute_script(a)
                time.sleep(0.5)
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                self.page_source = self.soup.select('#calender_data > div > table > tbody')
                dic['page_source'] = str(self.page_source)
                temp_img_src = self.soup.select('#calender_data > p > img')
                ab = datetime.datetime.now()
                date_now = ab.strftime('%Y%m%d%H%M%S')
                file_name = date_now + str(ab.microsecond)
                if len(temp_img_src) > 0:
                    temp_src = temp_img_src[0].attrs.get('src')
                    if '/images/mice/hico/common/noimg.gif' != temp_src:
                        encoding_url = parse.urlparse(temp_src[3:len(temp_src)])
                        print(encoding_url)
                        urllib.request.urlretrieve(
                            self.url_base + quote(encoding_url.path),
                            '../../originalDatas/' + file_name + '.png')
                        img_src = file_name + '.png'
                    else:
                        img_src = ''
                else:
                    img_src = ''
                dic['img_src'] = img_src
                print(dic['event_name'])
                self.cm.content_insert(dic, 'original')
                webdriver.ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

            if self.cnt != int(self.length):
                if page % 10 != 0:
                    if page <= 10:
                        # self.driver.find_element_by_xpath('//*[@id="sub_content"]/div[1]/div[1]/div[12]/div/a[1]').send_keys(Keys.ENTER)
                        self.driver.find_element_by_xpath(
                            '//*[@id="sub_content"]/div[1]/div[1]/div[{row}]/div/a[{page}]'.format(row=len(page_rows), page=self.cnt)).send_keys(Keys.ENTER)
                    else:
                        now_page = self.driver.find_element_by_xpath(
                            '//*[@id="sub_content"]/div[1]/div[1]/div[{}]/div/strong'.format(len(page_rows))).text
                        self.driver.find_element_by_xpath(
                            '//*[@id="sub_content"]/div[1]/div[1]/div[{row}]/div/a[{page}]'.format(row=len(page_rows), page=int(now_page)+2)).send_keys(Keys.ENTER)
                    self.cnt += 1
                else:
                    self.cnt += 1
                    page_length = self.driver.find_elements_by_xpath(
                        '//*[@id="sub_content"]/div[1]/div[1]/div[{}]/div/a'.format(len(page_rows)))
                    self.driver.find_element_by_xpath(
                        '//*[@id="sub_content"]/div[1]/div[1]/div[{row}]/div/a[{page}]'.format(row=len(page_rows), page=len(page_length)-1)).send_keys(Keys.ENTER)


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
