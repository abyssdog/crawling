from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
        self.cnt = 1
        self.row = 0
        self.col = 0
        self.soup = ''
        self.length = ''
        self.select_url = ''
        self.event_type = ''
        self.page_source = ''
        self.url = 'https://songdoconvensia.visitincheon.or.kr/sch/visitor/scinfo/event/UI-SC-0101-001Q.do' \
                   '?eventDivH=ALL&menuDiv=10&YYYYMM={year}{month}'
        self.url_page = 'https://songdoconvensia.visitincheon.or.kr/sch/visitor/scinfo/event/UI-SC-0101-003Q.do' \
                        '?lang=ko&addNo={page}'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        noncheck_results = self.crawl()  # 올해 행사일정 크롤링
        crawl_results = self.duplecate_check(noncheck_results)
        soreted_result = sorted(crawl_results, key=lambda crawl_result: crawl_result['event_start_date'])
        self.crawl_append(soreted_result)
        self.cm.close()
        self.driver.close()

    def crawl_append(self, crawl_results):
        for row in crawl_results:
            self.driver.get(row['source_url'])
            html = self.driver.page_source
            self.soup = Bs(html, 'html.parser')
            self.page_source = self.soup.select('body > div.wrap > div.contents > div.con > div > table > tbody')
            row['page_source'] = str(self.page_source)
            print(row['event_name'])
            self.cm.content_insert(row, 'original')

    def duplecate_check(self, check_lists):
        checked_list = []
        check = set([])
        # set에 넣어서 중복제거.
        for a in check_lists:
            check.add(a['source_url'])
        # Set과 check_lists에서 중복된거 찾아서 나머지 내용 추가
        for checked in check:
            for check_list in check_lists:
                if checked == check_list['source_url']:
                    checked_list.append(check_list)
                    break
        return checked_list

    def dic_insert(self, event_name, event_type, start_date, event_page_url, reg_date):
        dic = {
            'convention_name': 'songdoconvensia',
            'event_name': event_name,
            'event_type': event_type.replace("[", "").replace("]", ""),
            'event_start_date': datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
            'source_url': event_page_url,
            'home_page': 'https://songdoconvensia.visitincheon.or.kr/sch/main.do',
            'reg_date': reg_date
        }
        return dic

    def event_type_check(self, event):
        type = '행사'
        if event == 'ico_green':
            type = '전시'
        elif event == 'ico_blue':
            type = '회의'
        elif event == 'ico_red':
            type = '이벤트'
        return type

    def crawl(self):
        compare = []

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        self.driver.maximize_window()

        for month in range(1, 13):
            self.driver.get(self.url.format(year=now_year, month=str(month).zfill(2)))
            self.row = self.driver.find_elements_by_xpath('//*[@id="tab2"]/table/tbody/tr')
            for row in range(1, len(self.row)+1):
                self.col = self.driver.find_elements_by_xpath('//*[@id="tab2"]/table/tbody/tr[{}]/td'.format(row))
                for col in range(1, len(self.col)+1):
                    try:
                        event = WebDriverWait(self.driver, 0.5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a'.format(row=row, col=col))))
                        event_list = self.driver.find_elements_by_xpath('//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a'.format(row=row, col=col))
                        day = self.driver.find_element_by_xpath(
                            '//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/strong'.format(row=row, col=col)).text
                        if len(event_list) > 1:
                            for idx, event in enumerate(event_list):
                                href_tag = event.find_elements_by_xpath('//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a[{idx}]'.format(row=row, col=col, idx=idx+1))
                                event_page_url = href_tag[0].get_attribute('onclick')
                                pattern_url_value = r'\'([a-zA-Z0-9]*)\''
                                result_url_value = re.findall(pattern_url_value, event_page_url)
                                fin_url = self.url_page.format(page=result_url_value[1])
                                event_name = href_tag[0].get_attribute('text').strip()
                                start_date = now_year + '-' + str(month).zfill(2) + '-' + day.zfill(2)
                                temp_event_type = event.find_element_by_xpath('//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a[{idx}]'.format(row=row, col=col, idx=idx+1)).get_attribute('class')
                                event_type = self.event_type_check(temp_event_type.replace("'", ""))
                                dic = self.dic_insert(event_name, event_type, start_date, fin_url, reg_date)
                                compare.append(dic)
                        else:
                            event_name = event.text
                            href_tag = event.find_elements_by_xpath(
                                '//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a'.format(row=row, col=col))
                            event_page_url = href_tag[0].get_attribute('onclick')
                            pattern_url_value = r'\'([a-zA-Z0-9]*)\''
                            result_url_value = re.findall(pattern_url_value, event_page_url)
                            fin_url = self.url_page.format(page=result_url_value[1])
                            # event_name = href_tag[0].get_attribute('text').strip()
                            start_date = now_year + '-' + str(month).zfill(2) + '-' + day.zfill(2)
                            temp_event_type = event.find_element_by_xpath('//*[@id="tab2"]/table/tbody/tr[{row}]/td[{col}]/div/a'.format(row=row, col=col)).get_attribute('class')

                            event_type = self.event_type_check(temp_event_type.replace("'", ""))
                            dic = self.dic_insert(event_name, event_type, start_date, fin_url, reg_date)
                            compare.append(dic)
                    except TimeoutException:
                        continue
        return compare


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
