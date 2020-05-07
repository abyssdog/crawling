from crawling.api_naver import api_blog_first, api_cafe_first, api_web_first, api_blog_fullText, api_cafe_fullText, api_web_fullText
from datetime import datetime
import os
import crawl_counting
from crawling.image.image_google import CrawlingGoogleImage as cgi


def date():
    today_year = str(datetime.today().year)
    today_month = str(datetime.today().month)

    # all_api_crawler = 원문, all_api_fulltext = 전체 텍스트
    # names = ['all_api_crawler', 'all_api_fulltext']
    names = ['all_api_crawler']
    for name in names:
        today_year_folder = './originalDatas/{}/'.format(name) + today_year + '/'
        today_month_folder = today_year_folder + today_month

        if not os.path.isdir(today_year_folder):
            os.mkdir(today_year_folder)     # 년도 생성
            os.mkdir(today_month_folder)    # 달 생성

        elif not os.path.isdir(today_month_folder):
            os.mkdir(today_month_folder)


if __name__ == '__main__':
    date()
    search_list = ["반려동물", "반려동물이벤트", "반려동물행사", "반려동물교육", "반려동물자격증", "반려동물직업",
                   "반려동물산업", "반려동물상품"]
    # 조회 조건은 date:최신순, sim:정확도 2가지 있음.
    for key in search_list:
        api_blog_first.naver_blog_crawling(key, 100, "date")
    for key in search_list:
        api_cafe_first.naver_cafe_crawling(key, 100, "date")
    for key in search_list:
        api_web_first.naver_web_crawling(key, 100, "date")
    crawl_counting.run()
    #api_blog_fullText.run()
    #api_cafe_fullText.run()
    #api_web_fullText.run()
    cgi = cgi()
    #cgi.run()
