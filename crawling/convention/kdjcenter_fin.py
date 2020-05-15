from bs4 import BeautifulSoup as Bs
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


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'kdjcenter'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        # date format : 2020-00-00
        self.url = 'https://www.kdjcenter.or.kr/kor/eventSche' \
                   '?mode=list&menuId=151_163&sdate={now_start}&edate={now_end}'
        self.url_page = 'https://www.kdjcenter.or.kr/kor/eventSche' \
                        '?stype=A&sdate={now_start}&edate={now_end}&mode=view&menuId=151_163&type={type}&idx={idx}'
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        crawl_results = self.crawl()  # 올해 행사일정 크롤링
        self.crawl_append(crawl_results)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="viewForm"]/div[1]')))
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#viewForm > div.view_box > dl')
            self.page_source += self.soup.select('#viewForm > div.view_box > p')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        # 올해 년도 구하기
        now_year = self.now.strftime('%Y')
        now_month = self.now.strftime('%m')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        month_last_day = calendar.monthrange(int(now_year), 12)

        self.driver.get(self.url.format(now_start=now_year+'-01-01', now_end=now_year+'-12-'+str(month_last_day[1])))
        self.driver.maximize_window()

        # 페이지 길이 구하기
        first_page_size = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li')
        if len(first_page_size) == 4:
            self.length = 1
        elif len(first_page_size) < 8:
            self.length = self.driver.find_element_by_xpath(
                '//*[@id="pageLinkForm"]/a[{}]'.format(len(first_page_size) - 2)).text
            self.length = int(self.length) - 1
        else:
            self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[9]/a').click()
            self.length = self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[6]/strong').text
            self.length = int(self.length) - 1
            self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[1]/a').click()

        cnt = 0
        for page in range(1, int(self.length) + 1):
            time.sleep(0.5)
            content_length = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/div[1]/div[3]/ul/li')
            page_size = self.driver.find_elements_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li')
            for content in range(1, len(content_length) + 1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="content"]/div[2]/div[1]/div[3]/ul/li[{content}]/dl/dt/a'.format(content=content)
                )
                page_url_value = href_tag[0].get_attribute('onclick')
                url_value_pattern = r'\((.*)\)'
                url_value = re.findall(url_value_pattern, page_url_value)
                url_type = url_value[0][0:url_value[0].index(',')].replace("'", "").replace("\\", "")
                url_idx = url_value[0][url_value[0].index(',')+1:len(url_value[0])].replace("'", "").replace("\\", "").strip()
                event_page_url = self.url_page.format(now_start=now_year+'-01-01',
                                                      now_end=now_year+'-12-'+str(month_last_day[1]),
                                                      type=url_type,
                                                      idx=url_idx)
                event_name = href_tag[0].get_attribute('text')
                print(event_name)
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div[2]/div[1]/div[3]/ul/li[{content}]/dl/dd[1]'.format(content=content)).text
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div[2]/div[1]/div[3]/ul/li[{content}]/dl/dd[2]'.format(content=content)).text
                start_date = temp_date[0:temp_date.index('~')].strip()

                dic['convention_name'] = 'kdjcenter'
                dic['event_name'] = event_name
                dic['event_type'] = self.event_type
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'https://www.kdjcenter.or.kr/kor/'
                dic['reg_date'] = reg_date
                compare.append(dic)

            if self.cnt != int(self.length):
                cnt += 1
                if page % 5 != 0:
                    now_page = self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[{page}]/strong'.format(page=cnt+2)).text
                    self.driver.execute_script('linkPage({});'.format(int(now_page)+1))
                    self.cnt += 1
                else:
                    cnt = 0
                    self.cnt += 1
                    self.driver.find_element_by_xpath('//*[@id="content"]/div[2]/div[2]/ul/li[{page}]/a'.format(page=len(page_size)-1)).click()
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()

