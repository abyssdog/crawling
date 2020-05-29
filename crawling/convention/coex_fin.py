# coding=utf-8
from urllib import parse

from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import os
# import time
import urllib.request


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.convention_name = 'coex'
        self.cnt = 1
        self.goal_page = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'http://www.coex.co.kr/event-performance/total-schedule-2/page/{page}?type=visitor&sv&period=six_month&search_sdate={start_date}&search_edate={end_date}'

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
            self.page_source = self.soup.select('#primary > div > div > div > div > div.v-contents')
            event_type = self.soup.select('#primary > div > div > div > div > header > p.type > span')
            event_content = self.soup.select('#primary > div > div > div > div > div.v-contents > div.exhi-summary.clearfix > div.summary-desc')
            row['ctn'] = event_content[0].text
            row['page_source'] = str(self.page_source)
            row['event_type'] = event_type[0].text
            temp_img_src = self.soup.select('#primary > div > div > div > div > div.v-contents > div.exhi-info.clearfix > img')
            ab = datetime.datetime.now()
            date_now = ab.strftime('%Y%m%d%H%M%S')
            file_name = date_now + str(ab.microsecond)
            if len(temp_img_src) > 0:
                temp_src = temp_img_src[0].attrs.get('src')
                a = parse.urlparse(temp_src)
                print(a)
                urllib.request.urlretrieve(quote(temp_src), '../../originalDatas/' + file_name + '.png')
                img_src = file_name + '.png'
            else:
                img_src = ''
            row['img_src'] = img_src
            self.cm.content_insert(row, 'original')

    def crawl(self):
        compare = []
        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        self.driver.get(self.url.format(page=1, start_date='{year}-01-01'.format(year=now_year), end_date='{year}-12-30'.format(year=now_year)))
        self.driver.maximize_window()

        # 페이지 길이 구하기.
        pages = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a')
        last_page = self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a[{}]'.format(len(pages)-2)).text
        if int(last_page) == 10:
            self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a[{}]'.format(len(pages))).click()
            self.length = self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/span[2]').text
        else:
            self.length = self.driver.find_element_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/div/a[{}]'.format(len(pages)-1)).text

        for page in range(1, int(self.length)+1):
            self.driver.get(self.url.format(page=page, start_date='{year}-01-01'.format(year=now_year),
                                            end_date='{year}-12-30'.format(year=now_year)))
            contents = self.driver.find_elements_by_xpath('//*[@id="primary"]/div/div/div/div/dl/dd/ul/li')
            for content in range(1, len(contents)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{content}]/div/ul/li[2]/a'.format(
                        content=content)
                )
                event_page_url = href_tag[0].get_attribute('href')
                event_name = self.driver.find_element_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{content}]/div/ul/li[2]/a/span[1]'.format(content=content)
                ).text

                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="primary"]/div/div/div/div/dl/dd/ul/li[{content}]/div/ul/li[3]'.format(content=content)).text
                start_date = temp_date[0:temp_date.index('~')].strip()

                dic['convention_name'] = 'coex'
                dic['event_name'] = event_name.strip().replace(r'\n', '')
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['source_url'] = event_page_url
                dic['home_page'] = 'http://www.coex.co.kr/'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)
        print(compare)
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
#    crawl.run_crawl()
    a = parse.urlparse('http://210.116.77.61/wp-content/uploads/2020/05/코엑스-제출-엠블럼200507-300x198.png')
    q = parse.parse_qs(a.query)
    b = parse.urlencode(q, doseq=True)
    print(b)