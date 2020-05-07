import csv
import datetime
import pymysql


def run():
    print("start")
    start_time = datetime.datetime.now()
    end = csv_read()
    print(str(start_time)+" "+str(end))


# set 에 넣어서 중복을 제거후 list 로 넘긴다.
def csv_read():
    searches = ["반려동물", "반려동물이벤트", "반려동물행사", "반려동물교육", "반려동물자격증", "반려동물직업",
                "반려동물산업", "반려동물상품"]
    api_type = ["naver_blog", "naver_cafe", "naver_web"]
    today_year = str(datetime.datetime.today().year)
    today_month = str(datetime.datetime.today().month)
    today_day = str(datetime.datetime.today().day)
    target_date = '{}{}{}'.format(today_year, '0'+str(today_month) if int(today_month) < 10 else today_month, today_day)
    date = ''
    for api in api_type:
        for search in searches:
            data_list = []
            cnt = 0
            with open("C:/workSpace/flask_crawling/originalDatas/all_api_crawler/{y}/{m}/{d}_{a}_{s}.csv".format(
                    y=today_year, m=today_month, d=target_date, a=api, s=search), "r", encoding='utf-8', newline="") as file:
                reads = csv.reader(file)
                first_check = 0  # 첫행은 카테고리임.
                for row in reads:
                    if first_check != 0:
                        print(row)
                        data_list.append(row)
                        cnt += 1
                        if api == 'blog':
                            date = row[4]
                    first_check += 1
            save_content(data_list, api, date)
            save_result('{}-{}-{} 23:50:00'.format(today_year, today_month, today_day), api, cnt, search, 'text')
    end_time = datetime.datetime.now()
    return end_time


def save_content(datas, api, date):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = pymysql.connect(
        charset='utf8mb4',
        db='convention',
        host='localhost',
        password='dangam1234',
        port=3306,
        user='root'
    )
    curs = conn.cursor()
    query_event = """insert into naver_api
    (api_type, keyward, title, url, summary, reg_name, post_date, reg_date) 
    values(%s, %s, %s, %s, %s, %s, %s, %s)
    """
    for data in datas:
        curs.execute(query_event,
                     (api,
                      data[0],
                      data[1],
                      data[2],
                      data[3],
                      data[5],
                      date,
                      now
                      ))
    conn.commit()


def save_result(date, crawl_type, count, keyward, data_type):
    # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    crawl_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    conn = pymysql.connect(
        charset='utf8mb4',
        db='convention',
        host='localhost',
        password='dangam1234',
        port=3306,
        user='root'
    )
    curs = conn.cursor()
    query_event = """insert into crawled_data
    (crawl_date, crawl_type, crawl_amount, crawl_keyword, data_type) 
    values(%s, %s, %s, %s, %s)
    """
    curs.execute(query_event, (crawl_date, crawl_type, int(count), keyward, data_type))
    conn.commit()


if __name__ == '__main__':
    run()
