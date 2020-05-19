from bs4 import BeautifulSoup as Bs
from crawling.convention import conn_mysql as cm
from selenium import webdriver
from selenium.webdriver.common.by import By
import datetime
import os


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.url = 'http://www.at.or.kr/ac/event/acko311100/listList.action'
        self.convention_name = 'atcenter'
        self.soup = ''
        self.select_url = ''
        self.category = {
            5: '전시',
            7: '컨벤션',
            9: '박람회_행사',
            11: '공연_이벤트'
        }
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        crawl_result = self.crawl_atcenter()  # 올해 행사일정 크롤링
        select_result = self.content_select()  # 크롤링 해온 일정 전체 셀렉트
        for check_row in crawl_result:
            self.cm.content_insert(check_row, 'original')
        #checked_list = self.duplicate_check(crawl_result, select_result)  # 중복체크
        #self.get_page(crawl_result)  # 중복아닌 데이터 저장
        self.cm.close()
        self.driver.close()

    def crawl_atcenter(self):
        compare = []
        self.driver.get(self.url)
        self.driver.maximize_window()

        # 올해의 시간을 구함.
        now_year = self.now.strftime('%Y')
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        crawl_date = self.now.strftime('%Y%m%d')

        # 연간 행사일정 위해 해당 년도 입력
        self.driver.find_element(By.XPATH, '//*[@id="dP1"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="dP1"]').send_keys('{year}-01-01'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="dP2"]').clear()
        self.driver.find_element(By.XPATH, '//*[@id="dP2"]').send_keys('{year}-12-30'.format(year=now_year))
        self.driver.find_element(By.XPATH, '//*[@id="searchForm"]/div[1]/a').click()

        # atcenter의 각 행사일정은 div[4], 6 8 10 에 각각있다.
        for category in range(5, 12, 2):
            length = self.driver.find_elements_by_xpath(
                '//*[@id="printArea"]/div/div[{category}]/table/tbody/tr/th/a'.format(category=category))
            for tr in range(1, len(length)+1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="printArea"]/div/div[{category}]/table/tbody/tr[{tr}]/th/a'.format(
                        category=category, tr=tr)
                )
                print(href_tag[0].get_attribute('text'))
                event_page_url = href_tag[0].get_attribute('href')
                event_name = href_tag[0].get_attribute('text')
                temp_date = self.driver.find_element_by_xpath(
                    '//*[@id="printArea"]/div/div[{category}]/table/tbody/tr[{tr}]/td[1]'.format(
                        category=category, tr=tr)
                ).text
                start_date = temp_date[0:temp_date.index('~')].strip().replace('.', '-')
                self.driver.find_element_by_xpath(
                    '//*[@id="printArea"]/div/div[{category}]/table/tbody/tr[{tr}]/th/a'.format(
                        category=category, tr=tr)
                ).click()
                html = self.driver.page_source
                self.soup = Bs(html, 'html.parser')
                page_source = self.soup.select('#printArea > div > div.board > table > tbody > tr:nth-child(1)')
                page_source += self.soup.select('#printArea > div > div.board > table > tbody > tr.con')
                self.driver.back()

                dic['convention_name'] = 'atCenter'
                dic['event_name'] = event_name
                dic['event_type'] = self.category[category]
                dic['event_start_date'] = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                dic['page_source'] = str(page_source)
                dic['source_url'] = event_page_url
                dic['home_page'] = 'http://www.at.or.kr/home/acko000000/index.action'
                dic['reg_date'] = reg_date
                dic['crawl_version'] = crawl_date
                compare.append(dic)
        return compare

    # 일단 맨처음 크롤링한뒤에 해당년도의 새로운 행사를 체크해야되므로
    # 해당년도 것만 다 가져오기.
    def content_select(self):
        now_year = self.now.strftime('%Y-01-01')
        conn = self.cm.return_conn()
        curs = conn.cursor()
        sql = """SELECT * FROM event_original
        WHERE convention_name = 'atcenter' AND event_start_date > '{now}' """.format(now=now_year)
        if self.select_url != '':
            sql += """AND source_url = '{url}'""".format(url=self.select_url)
        curs.execute(sql)
        rows = curs.fetchall()  # 테이블이 존재안하면 len(rows) => 0
        self.select_url = ''  # 테이블이 존재하면 len(rows) => 1
        return rows

    def duplicate_check(self, check_lists, selected_tuples):
        end_list = []
        for check_row in check_lists:
            duplicate_flag = 0
            for selected_tuple in selected_tuples:
                if check_row.get('source_url') == selected_tuple[6]:
                    duplicate_flag += 1
            if duplicate_flag == 0:
                end_list.append(check_row.get('source_url'))
                self.cm.content_insert(check_row, 'original')
        return end_list

    def get_page(self, result_list):
        _dict = {}
        reg_date = self.now.strftime('%Y-%m-%d %H:%M:%S')
        for li in result_list:
            self.driver.get(li)  # li => Url
            html = self.driver.page_source
            soup = Bs(html, 'html.parser')
            data = soup.select('#printArea > div > div.board > table')
            self.select_url = li
            result = self.content_select()
            if len(result) > 0:
                event_id = result[0][0]
            else:
                event_id = -1
            _dict['convention_name'] = ''
            _dict['contents'] = ''
            _dict['page_source'] = str(data)
            _dict['source_url'] = ''
            _dict['home_page'] = ''
            _dict['reg_date'] = reg_date
            _dict['event_id'] = event_id
            if event_id != -1:
                self.cm.content_insert(_dict, 'page')


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
