# coding=utf-8
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
        self.convention_name = 'bexco'
        self.cnt = 1
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.base_url = 'http://www.bexco.co.kr'
        self.url = 'http://www.bexco.co.kr/kor//EventSchedule/main.do?mCode=MN0015'
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        crawl_results = self.crawl()  # 올해 행사일정 크롤링
        results = self.crawl_append(crawl_results)
        # fin_res = self.dc.duplicate_check(results, self.convention_name)
        # fin_res 를 insert를 시켜주면 된다.
        for res in results:
            self.cm.content_insert(res, 'original')
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('#contents > div.cont > div.view_wrap')
            event_cotent = self.soup.select('#contents > div.cont > div.view_wrap > div.detail_sec')
            row['ctn'] = event_cotent[0].text
            row['page_source'] = str(self.page_source)
            temp_img_src = self.soup.select('#contents > div.cont > div.view_wrap > div.info_sec > p > img')
            if len(temp_img_src) == 0:
                img_source = self.soup.select('#contents > div.cont > div.view_wrap > div.info_sec > p > a > img')
            else:
                img_source = temp_img_src
            ab = datetime.datetime.now()
            date_now = ab.strftime('%Y%m%d%H%M%S')
            file_name = date_now + str(ab.microsecond)
            if len(img_source) > 0:
                temp_src = img_source[0].attrs.get('src')
                urllib.request.urlretrieve(self.base_url + quote(temp_src), '../../originalDatas/' + file_name + '.png')
                img_src = file_name + '.png'
            else:
                img_src = ''
            row['img_src'] = img_src
            # self.cm.content_insert(row, 'original')
        return crawl_results

    def crawl(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        # now_date = self.now.date()
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')
        
        # 크롤링을 위해 탭 이동
        self.driver.find_element_by_xpath('//*[@id="contents"]/div[2]/div[4]/ul/li[2]/a').click()

        # 연간 행사일정 위해 해당 년도 입력
        self.driver.find_element(By.XPATH, '//*[@id="sch_start_date"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="sch_start_date"]').send_keys('{year}-01-01'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="sch_end_date"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="sch_end_date"]').send_keys('{year}-12-30'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div[5]/form/input[7]').click()

        # 페이지 길이 구하기.
        pages = self.driver.find_elements_by_xpath('//*[@id="forPrint"]/div[2]/div/a')
        if len(pages) == 12:
            self.driver.find_element_by_xpath('//*[@id="forPrint"]/div[2]/div/a[12]').click()
            self.length = self.driver.find_element_by_xpath('//*[@id="forPrint"]/div[2]/div/strong/span').text
            self.driver.find_element_by_xpath('//*[@id="forPrint"]/div[2]/div/a[1]').click()
        else:
            temp_length = self.driver.find_elements_by_xpath('//*[@id="forPrint"]/div[2]/div/a/span')
            self.length = self.driver.find_element_by_xpath(
                '//*[@id="forPrint"]/div[2]/div/a[{}]/span'.format(len(temp_length)-1)
            ).text

        for page in range(1, int(self.length)+1):
            contents = self.driver.find_elements_by_xpath('//*[@id="forPrint"]/div[1]/div/div/div[2]/strong/a')
            for content in range(1, len(contents)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="forPrint"]/div[1]/div/div[{content}]/div[2]/strong/a'.format(
                        content=content)
                )
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text')
                self.event_type = self.driver.find_element_by_xpath(
                    '//*[@id="forPrint"]/div[1]/div/div[{content}]/div[2]/p'.format(content=content)).text
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="forPrint"]/div[1]/div/div[{content}]/div[2]/dl/dd[2]'.format(content=content)).text
                start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-')
                event_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

                # if now_date < event_start_date:
                dic['convention_name'] = 'bexco'
                dic['event_name'] = event_name
                dic['event_type'] = self.event_type.replace("[", "").replace("]", "")
                dic['event_start_date'] = event_start_date
                dic['source_url'] = event_page_url
                dic['home_page'] = 'http://www.bexco.co.kr/kor/Main.do'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)

            if page < int(self.length)+1:
                if self.cnt < 10:
                    if page < 10:
                        self.driver.find_element_by_xpath(
                            '//*[@id="forPrint"]/div[2]/div/a[{}]'.format(self.cnt+1)).click()
                    else:
                        self.driver.find_element_by_xpath(
                            '//*[@id="forPrint"]/div[2]/div/a[{}]'.format(self.cnt+2)).click()
                    self.cnt += 1
                else:
                    self.cnt = 1
                    pagenation = self.driver.find_elements_by_xpath('//*[@id="forPrint"]/div[2]/div/a')
                    self.driver.find_element_by_xpath(
                        '//*[@id="forPrint"]/div[2]/div/a[{}]'.format(len(pagenation)-1)).click()
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
