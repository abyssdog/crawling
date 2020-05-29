import math
from urllib.parse import quote
from openpyxl import Workbook
from crawling.convention import conn_mysql as cm
from selenium import webdriver
import datetime
import os
import re
import time


def save(arr, key):
    keyset = {
        '{} 소모임'.format(key): 'A2362'
    }
    now = datetime.datetime.now()
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
    wb = Workbook()
    ws = wb.active
    # 첫행 입력
    ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
               '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
               '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드'))
    # DB 모든 데이터 엑셀로
    cnt = 0
    for row in arr:
        cnt += 1
        a = '{set}_{word}'.format(set=keyset[key+' 소모임'], word=key)
        b = row['cafe_name']
        c = row['cafe']
        d = row['cafe_summary']
        e = '인원수 : {:,}'.format(int(row['cafe_people']), ",")
        f = date_now
        g = '0'
        h = '{}카페'.format(row['cafe'])
        i = '재사용'
        j = '공개'
        k = '크롤링'
        al = 'http'
        m = row['cafe_url']
        n = 'www'
        o = '1'
        p = 'c'
        q = '이준재'
        r = '이준재'
        s = date_now
        t = date_now
        u = '#{first}, #{second}, #{third}'.format(first=key, second=key+' 소모임', third=row['cafe'])
        insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u)
        ws.append(insert)
        print(insert)
        # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
    wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(
        set=keyset[key+' 소모임'], word=key+' 소모임'))


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.cnt = 1
        self.goal_page = 8
        self.soup = ''
        self.compare = []
        self.length = ''
        self.url_naver = 'https://section.cafe.naver.com/cafe-home/search/cafes?query={keyword}'
        self.url_daum = 'http://top.cafe.daum.net/_c21_/' \
                        'search?search_opt=name&search_type=tab&sort_type=accu&q={keyword}&p={page}'

        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keywords = ['반려동물', '반려식물']
        portals = ['네이버', '다음']
        for keyword in keywords:
            self.compare = []
            for portal in portals:
                if portal == '네이버':
                    self.naver_crawl(keyword, portal)
                else:
                    self.daum_crawl(keyword, portal)
            save(self.compare, keyword)
        self.cm.close()
        self.driver.close()

    def daum_crawl(self, keyword, portal):
        time.sleep(0.5)
        temp_keyword = quote(keyword)
        self.driver.get(self.url_daum.format(keyword=temp_keyword, page=1))
        self.driver.maximize_window()

        total_page_object = self.driver.find_element_by_xpath('//*[@id="mArticle"]/div/div[1]/span').text
        pattern_page = r'약\s([0-9]*)건'
        temp_total_page = re.findall(pattern_page, total_page_object)
        self.length = math.ceil(int(temp_total_page[0])/10)

        for page in range(1, self.length+1):
            self.driver.get(self.url_daum.format(keyword=temp_keyword, page=page))
            time.sleep(0.5)
            content_length = self.driver.find_elements_by_xpath('//*[@id="mArticle"]/div/ul/li')

            for content in range(1, len(content_length) + 1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="mArticle"]/div/ul/li[{content}]/div[2]/strong/a'.format(content=content)
                )
                href_url = href_tag[0].get_attribute('href')
                href_name = href_tag[0].text
                cafe_summary = self.driver.find_element_by_xpath(
                    '//*[@id="mArticle"]/div/ul/li[{content}]/div[2]/p'.format(content=content)).text
                temp_people = self.driver.find_element_by_xpath(
                    '//*[@id="mArticle"]/div/ul/li[{content}]/div[2]/div[2]'.format(content=content)).text
                pattern_people = r'회원수\s?\:?\s?([0-9,]*)\s?\|'
                cafe_people = re.findall(pattern_people, temp_people)

                dic['cafe'] = portal
                dic['cafe_name'] = href_name
                print(href_name)
                dic['cafe_url'] = href_url
                dic['cafe_summary'] = cafe_summary
                dic['cafe_people'] = cafe_people[0].replace(',', '')
                self.compare.append(dic)

    def naver_crawl(self, keyword, portal):
        # 해당 키워드로 카페 목록 url 열기
        self.driver.get(self.url_naver.format(keyword=keyword))
        self.driver.maximize_window()

        # 조회할 카페 목록 조건 설정
        # sort
        self.driver.find_element_by_xpath('//*[@id="option_sort_form"]/fieldset/ul/li[3]/button/span').click()
        # ranking
        for z in range(2, 5+1):  # 나무 2, 열매 3, 가지 4, 잎새 5, 새싹 6, 씨앗 7
            self.driver.find_element_by_xpath('//*[@id="CAFESEARCH_RANKING"]/li[{}]/button/span'.format(z)).click()

        # 페이지 길이 구하기
        target_text = self.driver.find_element_by_xpath('//*[@id="content_srch"]/div[3]/div[1]/div/h3/span/em').text
        page_size = target_text.replace(',', '')
        self.length = math.ceil(int(page_size)/10)

        cnt = 0
        for page in range(1, self.length + 1):
            time.sleep(0.5)
            content_length = self.driver.find_elements_by_xpath('//*[@id="content_srch"]/div[3]/div[1]/ul/li')

            for content in range(1, len(content_length) + 1):
                dic = {}
                href_tag = self.driver.find_elements_by_xpath(
                    '//*[@id="content_srch"]/div[3]/div[1]/ul/li[{content}]/dl/dt/a'.format(content=content)
                )
                href_url = href_tag[0].get_attribute('href')
                href_name = href_tag[0].text
                cafe_summary = self.driver.find_element_by_xpath(
                    '//*[@id="content_srch"]/div[3]/div[1]/ul/li[{content}]/dl/dd[1]'.format(content=content)).text
                temp_people = self.driver.find_element_by_xpath(
                    '//*[@id="content_srch"]/div[3]/div[1]/ul/li[{content}]/dl/dd[2]'.format(content=content)).text
                pattern_people = r'멤버수\s?\:?\s?([0-9,]*)\·'
                cafe_people = re.findall(pattern_people, temp_people)

                dic['cafe'] = portal
                dic['cafe_name'] = href_name
                print(href_name)
                dic['cafe_url'] = href_url
                dic['cafe_summary'] = cafe_summary
                dic['cafe_people'] = cafe_people[0].replace(',', '')
                self.compare.append(dic)

            if page != int(self.length):
                self.cnt += 1
                cnt += 1
                if cnt < 7:
                    self.driver.find_element_by_xpath(
                        '//*[@id="content_srch"]/div[3]/div[2]/button[{page}]'.format(page=page+1)).click()
                else:
                    temp_page_length = self.driver.find_elements_by_xpath(
                        '//*[@id="content_srch"]/div[3]/div[2]/button')
                    if len(temp_page_length) == 12:
                        self.driver.find_element_by_xpath('//*[@id="content_srch"]/div[3]/div[2]/button[8]').click()
                    else:
                        self.driver.find_element_by_xpath(
                            '//*[@id="content_srch"]/div[3]/div[2]/button[{page}]'.format(page=self.goal_page)).click()
                        self.goal_page += 1


if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
