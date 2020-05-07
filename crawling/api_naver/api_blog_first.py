from urllib import parse, request
import csv
import datetime
import json
import math
import urllib
import os

import pymysql

naver_client_id = "9nneq4kHvUEuvIX6QNQn"
naver_client_secret = "SuPz6_Skzh"


def naver_blog_crawling(search_blog_keyword, display_count, sort_type):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/webkr?query=" + encode_search_keyword
    _request = urllib.request.Request(url)

    _request.add_header("X-Naver-Client-Id", naver_client_id)
    _request.add_header("X-Naver-Client-Secret", naver_client_secret)

    response = urllib.request.urlopen(_request)
    response_code = response.getcode()

    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))
            # 블로그 글 1000개 넘으면 1000개만 수집하게 됨
            if blog_pagination_total_count >= 1000:
                # 밑에 카운트 개수가 포스트 1000개 넘을때 따올 포스팅 수임
                blog_pagination_count = 1000
            else:
                blog_pagination_count = blog_pagination_total_count
            print("키워드 " + search_blog_keyword + " 에 해당하는 블로그 페이지 수 : " + str(blog_pagination_count))
        return blog_pagination_count


def content_insert(_dict):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='dangam1234',
        db='convention',
        charset='utf8mb4'
    )
    curs = conn.cursor()
    sql = """insert into naver_api
    (api_type, title, url, summary, content, reg_name, post_date, reg_date) 
    values(%s, %s, %s, %s, %s, %s, %s, %s)"""
    sql_insert = curs.execute(sql,
                              (_dict['api_type'],
                               _dict['title'],
                               _dict['url'],
                               _dict['summary'],
                               _dict['content'],
                               _dict['blogger_name'],
                               _dict['post_date'],
                               _dict['reg_date']
                               ))
    conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
    # print('commit success :', sql)
    conn.close()


def save():
    conn = pymysql.connect(
        charset='utf8',
        db='convention',
        host='127.0.0.1',
        password='dangam1234',
        port=3306,
        user='root'
    )
    curs = conn.cursor()
    sql = """insert """
    curs.execute(sql)
    data_count = curs.fetchall()


def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type):
    iter1 = 0
    header = ["keyword", "title", "url", "summary", "reg_date", "reg_user"]
    now = datetime.datetime.now()
    date_search = datetime.datetime.strftime(now, "%Y%m%d")
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)

    # 여기서 csv 저장 위치를 설정.
    # 경로 ex) 2020/4/blog_20200401_반려동물.csv
    # 리눅스 일때는 파일경로가 '/' 로 잡아야함.
    #with open(r"..\..\originalDatas\all_api_crawler\{y}\{m}\blog_{date}_{key}.csv".format(
    with open(r"./originalDatas/all_api_crawler/{y}/{m}/{date}_blog_{key}.csv".format(
            y=today_year, m=today_month, date=date_search, key=search_blog_keyword), "w", encoding='utf-8-sig', newline="") as file:
        encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(1, search_result_blog_page_count + 1, 100):
            url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
                display_count) + "&start=" + str(i) + "&sort=" + sort_type
            _request = urllib.request.Request(url)
            _request.add_header("X-Naver-Client-Id", naver_client_id)
            _request.add_header("X-Naver-Client-Secret", naver_client_secret)
            response = urllib.request.urlopen(_request)
            response_code = response.getcode()

            if response_code is 200:
                response_body = response.read()
                response_body_dict = json.loads(response_body.decode('utf-8'))

                for j in range(0, len(response_body_dict['items'])):
                    iter1 += 1
                    try:
                        blog_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")
                        blog_post_postdate = datetime.datetime.strptime(
                            response_body_dict['items'][j]['postdate'], "%Y%m%d").strftime("%Y-%m-%d")
                        #if date_now == blog_post_postdate:
                        if '2020-04-21' == blog_post_postdate:
                            writer.writerow([
                                search_blog_keyword,
                                response_body_dict['items'][j]['title'],
                                blog_post_url,
                                response_body_dict['items'][j]['description'],
                                blog_post_postdate,
                                response_body_dict['items'][j]['bloggername'],
                                ])
                    except Exception:
                        j += 1


if __name__ == '__main__':
    search_list = ["반려동물", "반려동물이벤트", "반려동물행사", "반려동물교육", "반려동물자격증", "반려동물직업",
                   "반려동물산업", "반려동물상품"]
    # 조회 조건은 date:최신순, sim:정확도 2가지 있음.
    for key in search_list:
        naver_blog_crawling(key, 100, "date")
