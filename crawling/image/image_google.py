from urllib.error import URLError
from urllib import request
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import datetime
import os
import time
import urllib


class CrawlingGoogleImage():
    def __init__(self):
        self.prefix = ["즐거운", "슬픈", "happy", "angry"]
        self.sufix = ["강아지", "dog"]
        self.dict = {}

    def run(self):
        for pre in self.prefix:
            for su in self.sufix:
                keyword = pre + " " + su
                count = self.crawl(keyword)

    def get_file_name(self):
        now = datetime.datetime.now()
        date_now = now.strftime('%Y%m%d%H%M%S')
        file_name = date_now + str(now.microsecond)
        return file_name

    def get_dir(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        #return_dir = os.path.join(base_dir, 'data')
        return_dir = os.path.relpath('crawling/originalDatas/all_image_crawler/2020/4', base_dir)
        return return_dir

    def crawl(self, search):
        res_dir = self.get_dir()
        url = "https://www.google.co.in/search?q={}&tbm=isch".format(search)
        browser = webdriver.Chrome('chromedriver.exe')
        browser.get(url)
        browser.set_window_size(1920, 1080)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        count = 0
        for cnt in range(1, 61):
            count += 1
            try:
                file_name = self.get_file_name()
                browser.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[{}]/a[1]'.format(cnt)).click()
                time.sleep(2)
                url_img = browser.find_element_by_xpath(
                    '//*[@id="Sva75c"]/div/div/div[3]/div[2]/div/div[1]/div[1]/div/div[2]/a/img'
                ).get_attribute('src')
                urllib.request.urlretrieve(url_img, res_dir+'\\'+file_name+'.png')
            except NoSuchElementException:
                pass
            except URLError:
                pass
        browser.close()
        return count


if __name__ == '__main__':
    # 구글의 크롤링 방지 정책으로 60개까지만 가져올수있음.
    # 그래서 키워드를 나눠서 가져옴. 각각 60개씩 가져옴. 4*2*60개
    cgi = CrawlingGoogleImage()
    for s in cgi.sufix:
        for p in cgi.prefix:
            cgi.crawl(p+" "+s)
    # a = cgi.get_dir()
    # print(a)
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # print(base_dir)
    # b = os.path.relpath('../../originalDatas', base_dir)
    # print(b)
    # print(os.path.abspath('../..//all_image_crawler/2020/4'))
