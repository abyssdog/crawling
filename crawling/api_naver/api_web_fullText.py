import csv
import datetime
import os
import time
import urllib
import requests
from urllib.error import HTTPError

import requests
from urllib3.exceptions import InsecureRequestWarning
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, UnexpectedAlertPresentException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib import request, parse


def run():
    start_time = datetime.datetime.now()
    end = duplicate_remove()
    print(str(start_time)+" "+str(end))


def get_headless_chrome():
    option = webdriver.ChromeOptions()
    option.add_argument('window-size=1920x1080')
    #option.add_argument('headless')
    option.add_argument('disable-gpu')
    option.add_argument(
         "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
    option.add_argument("lang=ko_KR")
    return option


def get_full_text1(resources_list):
    cnt = 0
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
    for resources in resources_list:
        cnt += 1
        result_text1 = ""
        try:
            resp = requests.get(resources[2], headers=headers, verify=False, timeout=60)
            soup1 = BeautifulSoup(resp.text)
            texts1 = soup1.findAll(text=True)
            visible_texts1 = filter(tag_visible, texts1)
            result_text1 = u" ".join(t.strip() for t in visible_texts1)
        except HTTPError:
            result_text1 = resources[3]
        except TimeoutError:
            result_text1 = resources[3]
        resources.append(result_text1)
    return resources_list


'''def get_full_text(resources_list):
    cnt = 0
    option = get_headless_chrome()
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=option)
    for resource in resources_list:
        fulltext = ""
        try:
            cnt += 1
            print(str(cnt) + " : " + resource[2] + " : " + resource[0] + " : " + resource[1])
            driver.get(resource[2])
            b = driver.switch_to.alert
            b.accept()
            fulltext = "alerted"
        except UnexpectedAlertPresentException:
            do = driver.switch_to.alert
            do.accept()
            fulltext = "alerted"
        except NoAlertPresentException:
            window_base = driver.current_window_handle
            window_list = driver.window_handles
            for window in window_list:
                if window != window_base:
                    driver.switch_to.window(window)
                    driver.close()
            driver.switch_to.window(window_base)
            fulltext = driver.find_element_by_tag_name("body").text
        resource.append(fulltext)
    driver.close()
    return resources_list
'''


def save(full_datas, search, count):
    cnt = 0
    header = ["keyword", "title", "url", "full_text", "reg_date", "reg_user"]
    now = datetime.datetime.now()
    date_search = datetime.datetime.strftime(now, "%Y%m%d")
    '''if count > 500:
        file_count = 2
    else:'''
    file_count = 1
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)
    # with open("../../originalDatas/all_api_fulltext/{y}/{m}/cafe_{d}_{k}.csv".format(
# for file_count in range(1, file_counts+1):
    with open("originalDatas/all_api_fulltext/{y}/{m}/{d}_web_{k}_{c}.csv".format(
            y=today_year, m=today_month, d=date_search, k=search, c=file_count), "w", encoding='utf-8-sig', newline="") as file:
        '''if cnt > len(full_datas):
            break'''
        writer = csv.writer(file)
        writer.writerow(header)
        try:
            for data in full_datas:
                writer.writerow([
                    data[0], data[1], data[2], data[6], data[4], data[5]
                ])
        except IndexError:  # 만약 풀텍스트를 가져오지 못하면 요약본이라도 넣어준다.
            writer.writerow([
                data[0], data[1], data[2], data[3], data[4], data[5]
            ])
        # cnt += 1


# set 에 넣어서 중복을 제거후 list 로 넘긴다.
def duplicate_remove():
    now = datetime.datetime.now()
    date_search = datetime.datetime.strftime(now, "%Y%m%d")
    searches = ["반려동물", "반려동물이벤트", "반려동물행사", "반려동물교육", "반려동물자격증", "반려동물직업",
                "반려동물산업", "반려동물상품"]
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)

    for search in searches:
        comparison_criteria = set()
        comparison_target = []
        result = []
        cnt = 0
        with open("originalDatas/all_api_crawler/{y}/{m}/{d}_web_{s}.csv".format(
                y=today_year, m=today_month, d=date_search, s=search), "r", encoding='utf-8', newline="") as file:
            reads = csv.reader(file)
            first_check = 0  # 첫행은 카테고리임.
            for row in reads:
                if first_check != 0:
                    comparison_criteria.add(row[1])  # set 에다가 넣음으로 중복 제거
                    comparison_target.append(row)
                    cnt += 1
                first_check += 1
        for target in comparison_target:
            for criteria in list(comparison_criteria):
                if target[1] == criteria:
                    result.append(target)
                    comparison_criteria.remove(criteria)
        full_data = get_full_text1(result)
        # cnt > 500 이면 저장되는 파일을 2개 만들도록 한다.
        save(full_data, search, cnt)
        print(search+' end')
    end_time = datetime.datetime.now()
    return end_time


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


if __name__ == '__main__':
    # run()
    print('web_api')
    '''    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    html = request.urlopen('https://www.klm.com/travel/kr_ko/prepare_for_travel/travel_planning/pets/index.htm').read()
    soup = BeautifulSoup(html, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    result_text = u" ".join(t.strip() for t in visible_texts)

    print(result_text)
'''