from bs4 import BeautifulSoup as Bs
from selenium.common.exceptions import TimeoutException

from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
import datetime
import os
import time


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'scc'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'https://www.scc.or.kr/events-3/'

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
            self.page_source = self.soup.select('#page-content > section.l-section.wpb_row.height_small.sidebar-fix.vc_hidden-xs > div > div > div > div > div > div:nth-child(3) > div.vc_col-sm-8.wpb_column.vc_column_container > div > div > div > div')
            self.page_source += self.soup.select(
                '#page-content > section.l-section.wpb_row.height_small.sidebar-fix.vc_hidden-xs > div > div > div > div > div > div:nth-child(7) > div.vc_col-sm-2.wpb_column.vc_column_container > div > div > div:nth-child(1) > div > p > strong')
            self.page_source += self.soup.select(
                '#page-content > section.l-section.wpb_row.height_small.sidebar-fix.vc_hidden-xs > div > div > div > div > div > div:nth-child(7) > div.vc_col-sm-10.wpb_column.vc_column_container > div > div > div:nth-child(1) > div')
            self.page_source += self.soup.select(
                '#page-content > section.l-section.wpb_row.height_small.sidebar-fix.vc_hidden-xs > div > div > div > div > div > div:nth-child(7) > div.vc_col-sm-2.wpb_column.vc_column_container > div > div > div:nth-child(5) > div > p > strong')
            self.page_source += self.soup.select(
                '#page-content > section.l-section.wpb_row.height_small.sidebar-fix.vc_hidden-xs > div > div > div > div > div > div:nth-child(7) > div.vc_col-sm-10.wpb_column.vc_column_container > div > div > div.w-post-elm.post_custom_field.type_text.color_link_inherit > a')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')

        # 행사일정 페이지 접속후 리스트 페이지로 이동.
        self.driver.find_element_by_xpath('//*[@id="calendar"]/div/div/div/div/div/div[2]/div[1]/div/div[2]/div').click()

        # 전체 일정 볼수있도록 조절
        while True:
            try:
                wait = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="us_grid_1"]/div[2]/a/span')))
                if wait.text == '더 보기':
                    wait.click()
                else:
                    break
            except TimeoutException:
                # self.driver.execute_script("arguments[0].click();", element)
                break
        # 전체 일정 목록 길이
        time.sleep(2)
        self.length = self.driver.find_elements_by_xpath('//*[@id="us_grid_1"]/div[1]/article')

        for content in range(1, len(self.length) + 1):
            dic = {}
            href_tag = self.driver.find_elements_by_xpath(
                '//*[@id="us_grid_1"]/div[1]/article[{content}]/div/div/div[2]/h2/a'.format(content=content))
            event_page_url = href_tag[0].get_attribute('href')
            event_name = href_tag[0].get_attribute('text').strip()
            temp_date = self.driver.find_element_by_xpath(
                '//*[@id="us_grid_1"]/div[1]/article[{content}]/div/div/div[2]/div[2]'.format(
                    content=content)).text
            start_date = temp_date[0:temp_date.index('~')].strip()
            self.event_type = self.driver.find_element_by_xpath(
                '//*[@id="us_grid_1"]/div[1]/article[{content}]/div/div/div[2]/div[1]/span'.format(content=content)).text

            dic['convention_name'] = 'scc'
            dic['event_name'] = event_name
            dic['event_type'] = self.event_type.replace("[", "").replace("]", "")
            dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            dic['source_url'] = event_page_url
            dic['home_page'] = 'https://www.scc.or.kr/'
            dic['reg_date'] = reg_date
            compare.append(dic)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()

