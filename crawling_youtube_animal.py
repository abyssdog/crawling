from crawling.convention import conn_mysql as cm
from openpyxl import Workbook
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import datetime
import os
import time


class CrawlClass(object):
    def __init__(self):
        self.cm = cm.CrawlClass()
        self.now = datetime.datetime.now()
        self.cnt = 0
        self.length = ''
        self.url_a = 'https://www.youtube.com/results?search_query=%EB%B0%98%EB%A0%A4%EB%8F%99%EB%AC%BC&sp=CAMSAhAC'
        self.url_p = 'https://www.youtube.com/results?search_query=%EC%8B%9D%EB%AC%BC&sp=CAMSAhAC'
        
        self.option = webdriver.ChromeOptions()
        self.option.add_argument('window-size=1920x1080')
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=self.option)

    def run_crawl(self):
        keyword = ['반려동물', '반려식물']
        for key in keyword:
            a = self.crawl(key)
            self.save(a, key)
        self.cm.close()
        self.driver.close()

    def crawl(self, key):
        res = []

        if key == '반려동물':
            self.driver.get(self.url_a)
        else:
            self.driver.get(self.url_p)
        self.driver.maximize_window()
        time.sleep(0.5)

        while True:
            try:
                time.sleep(0.5)
                last = self.driver.find_element_by_xpath('//*[@id="contents"]/ytd-message-renderer').text
                if last == '결과가 더 이상 없습니다.':
                    break
            except NoSuchElementException:
                ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()

        length = self.driver.find_elements_by_xpath('//*[@id="contents"]/ytd-channel-renderer')
        for content in range(1, len(length)+1):
            di = {}
            youtube_name = self.driver.find_element_by_xpath(
                '/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/'
                'div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/'
                'ytd-channel-renderer[{content}]/div/div[2]/a/div[1]/ytd-channel-name/div/div/'
                'yt-formatted-string'.format(content=content)).text
            href_tag = self.driver.find_elements_by_xpath(
                '/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/'
                'div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/'
                'ytd-channel-renderer[{content}]/div/div[2]/a'.format(
                    content=content))
            youtube_url = href_tag[0].get_attribute('href')
            youtube_ctn = self.driver.find_element_by_xpath(
                '/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/'
                'div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/'
                'ytd-channel-renderer[{content}]/div/div[2]/a/div[1]/yt-formatted-string'.format(
                    content=content)).text
            youtube_people = self.driver.find_element_by_xpath(
                '/html/body/ytd-app/div/ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/'
                'div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/'
                'ytd-channel-renderer[{content}]/div/div[2]/a/div[1]/div/span[1]'.format(
                    content=content)).text
            di['youtube_name'] = youtube_name
            di['youtube_url'] = youtube_url
            di['youtube_ctn'] = youtube_ctn
            di['youtube_people'] = youtube_people
            res.append(di)
        return res

    def save(self, arr, key):
        keyset = {
            '반려동물 동영상': 'A2383',
            '반려식물 동영상': 'P2373'
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
        for row in arr:
            self.cnt += 1
            a = '{set}_{word}'.format(set=keyset['{} 동영상'.format(key)], word=str(self.cnt).zfill(4))
            b = row['youtube_name']
            c = '유투브'
            d = row['youtube_ctn']
            e = row['youtube_people']
            f = date_now
            g = '0'
            h = '유투브'
            i = '재사용'
            j = '공개'
            k = '크롤링'
            al = 'http'
            m = row['youtube_url']
            n = 'www'
            o = '1'
            p = 'c'
            q = '이준재'
            r = '이준재'
            s = date_now
            t = date_now
            u = '#{key}, #동영상, #{key} 동영상'.format(key=key)
            insert = (a, b, c, d, e, f, g, h, i, j, k, al, m, n, o, p, q, r, s, t, u)
            ws.append(insert)
        wb.save('C:/workSpace/flask_crawling/originalDatas/{set}_{word}.xlsx'.format(
            set=keyset['{} 동영상'.format(key)], word=key+' 동영상'))
        

if __name__ == '__main__':
    crawl = CrawlClass()
    crawl.run_crawl()
