from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import os
import re

_dict = {}


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'ceco'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'https://www.ceco.co.kr/bbx/board.php?bx_table=01_01'

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
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#bo_v_atc')
            row['page_source'] = str(self.page_source)
            self.cm.content_insert(row, 'original')

    def crawl(self):
        first = 1
        second = 1
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        # 연간 행사일정 위해 해당 년도 입력
        self.driver.find_element(By.XPATH, '//*[@id="sdate"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="sdate"]').send_keys('{year}-01-01'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="edate"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="edate"]').send_keys('{year}-12-30'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="bo_sch"]/form/div[2]/button').click()

        # 페이지 길이 구하기.
        pages = self.driver.find_elements_by_xpath('//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a')
        if len(pages) < 12:
            temp_length = self.driver.find_elements_by_xpath(
                '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[{}]'.format(len(pages) - 2))
            self.length = temp_length[0].text
        else:
            self.driver.find_element_by_xpath(
                '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[{}]'.format(len(pages) - 1)).click()
            self.length = self.driver.find_element_by_xpath(
                '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/strong').text
            self.driver.find_element_by_xpath('//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[1]').click()

        for page in range(1, int(self.length)+1):
            contents = self.driver.find_elements_by_xpath('//*[@id="gall_ul"]/li')
            for content in range(1, len(contents)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]/a[2]'.format(
                        content=content)
                )
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text')
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]/a[1]'.format(content=content)).text
                temp_date = self.driver.find_elements_by_xpath(
                    '//*[@id="gall_ul"]/li[{content}]/div/div[2]/div[2]'.format(content=content))
                pattern_date = r'\n(([0-9]*)-([0-9]*)-([0-9]*))'
                temp_date2 = re.findall(pattern_date, temp_date[0].text)
                start_date = temp_date2[0][0]

                dic['convention_name'] = 'ceco'
                dic['event_name'] = event_name.strip().replace(r'\n', '')
                dic['event_type'] = self.event_type
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'https://www.ceco.co.kr/'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)

            if page % 10 != 0:
                now_page = self.driver.find_element_by_xpath('//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/strong').text
                if int(now_page) == 1:
                    self.goal_page = 1
                    self.cnt += 1
                elif int(now_page) == 2:
                    self.goal_page = 3
                    self.cnt += 1
                else:
                    self.cnt += 1
                    self.goal_page += 1

                if page < 10:
                    self.driver.find_element_by_xpath(
                        '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[{}]'.format(self.goal_page)).click()
                else:
                    self.driver.find_element_by_xpath(
                        '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[{}]'.format(self.goal_page)).click()
            else:
                self.cnt += 1
                self.goal_page = 2
                self.driver.find_element_by_xpath(
                    '//*[@id="wrap_content"]/div/div[2]/div[2]/nav/span/a[11]').click()
        print(compare)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
