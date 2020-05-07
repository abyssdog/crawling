import csv
import time

import pymysql
from bs4 import BeautifulSoup
import requests
from openpyxl import Workbook
import ssl
from urllib.request import urlopen


def run():
    category = ['agent', 'hospital', 'production', 'importation', 'sales',
                'exhibition', 'management', 'transportation', 'beauty', 'funeral']
    res = []
    page = {
        'agent': 356, 'hospital': 482, 'production': 178,
        'importation': 8, 'sales': 420, 'exhibition': 61,
        'management': 408, 'transportation': 52, 'beauty': 672, 'funeral': 5
    }
    url = {
        'agent': 'https://okminwon.pqis.go.kr/minwon/information/statistics.html?statsType=102&frYear=2020&frMonth=04&toYear=2020&toMonth=04&trnType=IN&metType=hwa&natCd=128&natNm=%EC%9D%BC%EB%B3%B8&x=40&y=5'
    }
    context = ssl._create_unverified_context()
    time.sleep(2)
    #response = requests.get(url['agent'])
    response = urlopen(url['agent'], context=context)
    soup = BeautifulSoup(response.read(), 'html.parser')
    table = soup.find('table')
    trs = table.find_all_next('tr')
    print(trs)
    cnt = 0

    #save(res)


def content_insert(_dict, category):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='dangam1234',
        db='convention',
        charset='utf8mb4'
    )
    curs = conn.cursor()
    sql = """insert into animal_company
    (company, ceo, phone, address, {c}, home_page) 
    values(%s, %s, %s, %s, %s, %s)""".format(c=category)
    sql_insert = curs.execute(sql,
                              (_dict['company'],
                               _dict['ceo'],
                               _dict['phone'],
                               _dict['address'],
                               'y',
                               _dict['home_page']
                               ))
    conn.commit()  # 만약에 아니면 ttl, srchtml 두개만 넣어도 되는듯. 호출은 두개만 함.
    # print('commit success :', sql)
    conn.close()


def save():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='dangam1234',
        db='convention',
        charset='utf8mb4'
    )
    curs = conn.cursor()
    sql = """select * from animal_company 
    """
    curs.execute(sql)
    rs = curs.fetchall()
    header = ["no", "company", "ceo", "phone", "address"]
    file_count = 1
    wb = Workbook()
    ws = wb.active
    # 첫행 입력
    ws.append(('번호', '회사이름', '사장', '전화번호', '주소', '홈페이지'))
    # DB 모든 데이터 엑셀로
    for row in rs:
        ws.append(row)
    wb.save('C:/workSpace/flask_crawling/originalDatas/동물업체.xlsx')


if __name__ == '__main__':
    run()
