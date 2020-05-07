import csv
import datetime
import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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
    option.add_argument('headless')
    option.add_argument('disable-gpu')
    option.add_argument(
         "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
    option.add_argument("lang=ko_KR")
    return option


# 이번 테스트 끝나면 cnt 만들어서 100정도면 쌓고 컷
def get_full_text1(resources_list):
    option = get_headless_chrome()
    driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver.exe"), options=option)
    cnt = 0
    for resource in resources_list:
        # daum 블로그 내용이 소수지만 있음.
        flag_daum = resource[2].find('http://blog.daum')
        if flag_daum != -1:
            try:
                cnt += 1
                print(str(cnt) + " : " + resource[0] + " : " + resource[1])
                driver.get(resource[2])
                driver.maximize_window()
                driver.switch_to.frame('BlogMain')
                frameset = driver.find_elements_by_tag_name('iframe')
                driver.switch_to.frame(frameset[1])
                fulltext = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="contentDiv"]'))).text
                resource.append(fulltext)
            except Exception:
                continue
        else:
            try:
                cnt += 1
                print(str(cnt) + " : " + resource[0] + " : " + resource[1])
                driver.get(resource[2])
                driver.maximize_window()
                driver.switch_to.default_content()
                driver.switch_to.frame('mainFrame')
                fulltext = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="printPost1"]/tbody/tr/td[2]/div/div[1]'))).text
                resource.append(fulltext)
            except Exception:
                continue
    driver.close()
    return resources_list


def get_full_text(resources_list):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    cnt = 0
    for resource in resources_list:
        cnt += 1
        print(str(cnt) + " : " + resource[0]+" : "+resource[1])
        html = request.urlopen(resource[2]).read()
        soup = BeautifulSoup(html, 'lxml')
        for link in soup.select('#mainFrame'):
            real_blog_post_url = "http://blog.naver.com" + link.get('src')
            get_real_blog_post_content_code = requests.get(real_blog_post_url, headers=headers)
            get_real_blog_post_content_text = get_real_blog_post_content_code.text

            get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')
            for blog_post_content in get_real_blog_post_content_soup.select('#printPost1'):
                blog_post_content_text = blog_post_content.get_text()
                blog_post_full_contents = str(blog_post_content_text)
                resource.append(blog_post_full_contents)
    return resources_list


def save(full_datas, search, count):
    header = ["keyword", "title", "url", "full_text", "reg_date", "reg_user"]
    now = datetime.datetime.now()
    date_search = datetime.datetime.strftime(now, "%Y%m%d")
    '''if count > 500:
        file_count = 2
    else:'''
    file_count = 1
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)
# for file_count in range(1, file_counts+1):
    with open("../../originalDatas/all_api_fulltext/{y}/{m}/blog_{d}_{k}.csv".format(
            y=today_year, m=today_month, d=date_search, k=search, c=file_count), "w", encoding='utf-8-sig', newline="") as file:
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
        with open("originalDatas/all_api_crawler/{y}/{m}/{d}_blog_{s}.csv".format(
                y=today_year, m=today_month, d=date_search, s=search), "r", encoding='utf-8', newline="") as file:
        # with open('../../originalDatas/all_api_crawler/{y}/{m}/blog_20200402_반려동물.csv'.format(
        # y=today_year, m=today_month), "r", encoding='utf-8', newline="") as file:
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
        #full_data = get_full_text(result)
        full_data = get_full_text1(result)
        save(full_data, search, cnt)
        print(search+' end')
    end_time = datetime.datetime.now()
    return end_time


if __name__ == '__main__':
    # start = datetime.datetime.now()
    # print(str(start) + ": start")
    run()