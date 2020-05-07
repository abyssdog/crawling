import re
import json
import math
import datetime
import requests
import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
from datetime import timedelta
import pymysql

#용택 여기따가 적으셈 니 api 키 값
naver_client_id = "9nneq4kHvUEuvIX6QNQn"
naver_client_secret = "SuPz6_Skzh"
_dict = {}


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
    (title, url, summary, content, reg_name, post_date, reg_date) 
    values(%s, %s, %s, %s, %s, %s, %s)"""
    sql_insert = curs.execute(sql,
                              (_dict['post_title'],
                               _dict['post_url'],
                               _dict['summary'],
                               _dict['post_content'],
                               _dict['blogger_name'],
                               _dict['post_date'],
                               _dict['reg_date']
                               ))
    conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
    # print('commit success :', sql)
    conn.close()


def naver_blog_crawling(search_blog_keyword, display_count, sort_type):
    search_result_blog_page_count = get_blog_search_result_pagination_count(search_blog_keyword, display_count)
    get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type)


def get_blog_search_result_pagination_count(search_blog_keyword, display_count):
    encode_search_keyword = urllib.parse.quote(search_blog_keyword)
    url = "https://openapi.naver.com/v1/search/webkr?query=" + encode_search_keyword
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", naver_client_id)
    request.add_header("X-Naver-Client-Secret", naver_client_secret)

    response = urllib.request.urlopen(request)
    response_code = response.getcode()

    if response_code is 200:
        response_body = response.read()
        response_body_dict = json.loads(response_body.decode('utf-8'))

        if response_body_dict['total'] == 0:
            blog_pagination_count = 0
        else:
            blog_pagination_total_count = math.ceil(response_body_dict['total'] / int(display_count))
            # 블로그 글 1000개 넘으면 1000개만 수집하게 됨
            #if blog_pagination_total_count >= 1000:
                # 밑에 카운트 개수가 포스트 1000개 넘을때 따올 포스팅 수임
            #    blog_pagination_count = 1000
            #else:
            #    blog_pagination_count = blog_pagination_total_count
            blog_pagination_count = blog_pagination_total_count

            print("키워드 " + search_blog_keyword + " 에 해당하는 포스팅 수 : " + str(response_body_dict['total']))
            print("키워드 " + search_blog_keyword + " 에 해당하는 블로그 페이지 수 : " + str(blog_pagination_total_count))
            print("키워드 " + search_blog_keyword + " 에 해당하는 블로그 처리할 수 있는 페이지 수 : " + str(blog_pagination_count))

        return blog_pagination_count


def get_blog_post(search_blog_keyword, display_count, search_result_blog_page_count, sort_type):
    iter1 = 0
    #여기 내 경로로 해놨는데, 너꺼에 맞게 바꿔 써 텍스트 파일 파싱해주는 거임
    file = open("C:/workSpace/crawl_blog_date1.txt","w", encoding='utf-8')
    encode_search_blog_keyword = urllib.parse.quote(search_blog_keyword)

    for i in range(1, search_result_blog_page_count + 1, 7):
    #for i in range(1, 70, 7):
    #for i in range(1, 14, 7):
        url = "https://openapi.naver.com/v1/search/blog?query=" + encode_search_blog_keyword + "&display=" + str(
            display_count) + "&start=" + str(i) + "&sort=" + sort_type
        request = urllib.request.Request(url)

        request.add_header("X-Naver-Client-Id", naver_client_id)
        request.add_header("X-Naver-Client-Secret", naver_client_secret)
        if i == 1380:
            print(1380)
        response = urllib.request.urlopen(request) # 1388번째에서 에러남
        response_code = response.getcode()
        now = datetime.datetime.now()
        reg_date = now.strftime('%Y-%m-%d %H:%M:%S')
        if response_code is 200:
            response_body = response.read()
            response_body_dict = json.loads(response_body.decode('utf-8'))

            for j in range(0, len(response_body_dict['items'])):

                try:
                    blog_post_url = response_body_dict['items'][j]['link'].replace("amp;", "")

                    get_blog_post_content_code = requests.get(blog_post_url)
                    get_blog_post_content_text = get_blog_post_content_code.text
                    # 여기서 에러남
                    get_blog_post_content_soup = BeautifulSoup(get_blog_post_content_text, 'lxml')

                    for link in get_blog_post_content_soup.select('#mainFrame'):
                        #print(str(j)+" : 저장되는거")
                        real_blog_post_url = "http://blog.naver.com" + link.get('src')

                        get_real_blog_post_content_code = requests.get(real_blog_post_url)
                        get_real_blog_post_content_text = get_real_blog_post_content_code.text

                        get_real_blog_post_content_soup = BeautifulSoup(get_real_blog_post_content_text, 'lxml')

                        #for blog_post_content in get_real_blog_post_content_soup.select('div#postViewArea'):
                        for blog_post_content in get_real_blog_post_content_soup.select('#printPost1'):
                            #blog_post_content_text = blog_post_content.get_text()
                            postDate = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'], '%Y%m%d')
                            now = datetime.datetime.now()
                            month = now + timedelta(days=-90)

                            remove_html_tag = re.compile('<.*?>')
                            blog_post_title = re.sub(remove_html_tag, '', response_body_dict['items'][j]['title'])
                            blog_post_description = re.sub(remove_html_tag, '',
                                                           response_body_dict['items'][j]['description'])
                            blog_post_postdate = datetime.datetime.strptime(response_body_dict['items'][j]['postdate'],
                                                                            "%Y%m%d").strftime("%y.%m.%d")
                            blog_post_blogger_name = response_body_dict['items'][j]['bloggername']
                            #blog_post_full_contents = str(blog_post_content_text)
                            iter1 = iter1 + 1
                            _dict['post_title'] = blog_post_title
                            _dict['post_url'] = blog_post_url
                            _dict['summary'] = blog_post_description
                            #_dict['post_content'] = blog_post_full_contents
                            _dict['blogger_name'] = blog_post_blogger_name
                            _dict['post_date'] = blog_post_postdate
                            _dict['reg_date'] = reg_date
                            if blog_post_postdate == "20.01.01":
                                print("포스팅 URL : {}".format(blog_post_url))
                                print("포스팅 제목  : {}".format(blog_post_title))
                                print("포스팅 설명  : {}".format(blog_post_description))
                                print("포스팅 날짜  : {}".format(blog_post_postdate))
                                print("블로거 이름  : {}".format(blog_post_blogger_name))
                                #print("포스팅 내용  : {}".format(blog_post_full_contents))
                            #content_insert(_dict)
                            #file.write("포스팅 URL : " + blog_post_url + '\n')
                            #file.write("포스팅 제목 : " + blog_post_title + '\n')
                            #file.write("포스팅 설명 : " + blog_post_description + '\n')
                            #file.write("포스팅 날짜 : " + blog_post_postdate + '\n')
                            #file.write("블로거 이름 : " + blog_post_blogger_name  + '\n')
                            #file.write("포스팅 내용 : " + blog_post_full_contents + '\n\n\n\n')
                            print("{a} : {b}".format(a=iter1, b=blog_post_postdate))
                except:
                    j += 1
    file.close()


if __name__ == '__main__':
    # 블로그는 한페이지에 7개
    # naver_blog_crawling("펫 박람회", 7, "date")
    naver_blog_crawling("반려동물", 10, "date")