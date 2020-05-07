from urllib import parse, request
import csv
import datetime
import json
import math
import pymysql
import re
import urllib

naver_client_id = "9nneq4kHvUEuvIX6QNQn"
naver_client_secret = "SuPz6_Skzh"


def naver_cafe_crawling(search_blog_keyword, display_count, sort_type):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/cafearticle?query=" + encode_search_keyword
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
        return blog_pagination_count


def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type):
    header = ["keyword", "title", "url", "summary", "reg_date", "reg_user"]
    now = datetime.datetime.now()
    date_search = datetime.datetime.strftime(now, "%Y%m%d")
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)

    #with open("/home/all_api_crawler/{y}/{m}/cafe_{date}_{key}.csv".format(
    with open(r"originalDatas\all_api_crawler\{y}\{m}\{date}_cafe_{key}.csv".format(
            y=today_year, m=today_month, date=date_search, key=search_blog_keyword), "w", encoding='utf-8-sig',
            newline="") as file:
        encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)
        writer = csv.writer(file)
        writer.writerow(header)
        for i in range(1, search_result_blog_page_count + 1, 100):
            url = "https://openapi.naver.com/v1/search/cafearticle?query=" + encode_search_blog_keyword + \
                  "&display=" + str(display_count) + "&start=" + str(i) + "&sort=" + sort_type
            _request = urllib.request.Request(url)
            _request.add_header("X-Naver-Client-Id", naver_client_id)
            _request.add_header("X-Naver-Client-Secret", naver_client_secret)

            response = urllib.request.urlopen(_request)
            response_code = response.getcode()
            if response_code is 200:
                response_body = response.read()
                response_body_dict = json.loads(response_body.decode('utf-8'))

                for j in range(0, len(response_body_dict['items'])):
                    try:
                        cafe_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")
                        remove_html_tag = re.compile('<.*?>')
                        post_title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                        summary = re.sub(remove_html_tag, '',
                                         response_body_dict['items'][j]['description'])
                        reg_name = response_body_dict['items'][j]['cafename']
                        writer.writerow([
                            search_blog_keyword,
                            post_title,
                            cafe_post_url,
                            summary,
                            '',
                            reg_name,
                        ])
                    except Exception:
                        j += 1
    file.close()


if __name__ == '__main__':
    search = ["반려동물", "반려동물이벤트", "반려동물행사", "반려동물교육", "반려동물자격증", "반려동물직업",
              "반려동물산업", "반려동물상품"]
    for s in search:
        naver_cafe_crawling(s, 100, "date")
'//*[@id="post_1912"]/div/div[1]/div[2]/table/tbody/tr/td[2]'
'//*[@id="post_13960848"]/div/div[1]/div[2]/table/tbody/tr/td[2]'