import csv
import datetime
import re
import time

import pymysql
from bs4 import BeautifulSoup
import requests
from openpyxl import Workbook


def run():
    category = ['pqi']
    res = []
    page = {
        'pqi': 3861
    }
    url = {
        'pqi': 'https://www.pqi.or.kr/inf/qul/infQulList.do'
    }
    #for page in range(1, page['pqi']+1):
    for page in range(1, 2):
        response = requests.get(url['pqi'].format(page))
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('#qulListTb')
        trs = table.find_all_next('tr')
        cnt = 0
        for idx, tr in enumerate(trs):
            if idx > 0:
                arr = {}
                cnt += 1
                tds = tr.find_all('td')
                # agent

                #content_insert(arr, temp)
                print('{}{}{}{}{}'.format(cnt, arr['company'], arr['ceo'], arr['phone'], arr['address']))
    #save(res)


def content_insert(_dict, category):
    conn = pymysql.connect(
        db='yojido', user='yojido', password='dg202004@#',
        host='dev.thegam.io', port=3306, charset='utf8mb4'
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
    now = datetime.datetime.now()
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
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
    WHERE exhibition = 'y'
    """
    curs.execute(sql)
    rs = curs.fetchall()
    file_count = 1
    wb = Workbook()
    ws = wb.active
    # 첫행 입력
    ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
               '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
               '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드'))
    # DB 모든 데이터 엑셀로
    cnt = 0
    for row in rs:
        cnt += 1
        temp_str = row[4]
        try:
            pre_pattern = r"^([\w]*)[시|도]"  # row[3] => 페이지소스
            pre = re.search(pre_pattern, temp_str)
            su = temp_str[pre.end():]
            c_var = pre.group()
            d_var = su.strip()
        except AttributeError:
            if len(temp_str) > 1:
                pre_pattern = r"^([\w]*)[\s]"  # row[3] => 페이지소스
                pre = re.search(pre_pattern, temp_str)
                su = temp_str[pre.end():]
                c_var = pre.group()
                d_var = su.strip()
            else:
                c_var = '-'
                d_var = '-'
        a = 'A2221_' + str(cnt).rjust(4, '0')  # ok
        b = row[1]  # 여기에 업체명
        c = c_var  # 여기에는 지역 대구분 ex) 시, 도
        d = d_var  # 여기는 지역 소구분 ex) 구 동
        if row[3] == '-':
            e = '-'
        else:
            e = row[3]
        f = date_now
        g = '0'
        h = '동물보호관리시스템'
        i = '재사용'
        j = '공개'
        k = '크롤링'
        l = 'http'
        m = 'https://www.animal.go.kr/front/awtis/shop/salesList.do?sWrkCd=D&menuNo=6000000010'
        n = 'www'
        o = '1'
        p = 'c'
        q = '이준재'
        r = '이준재'
        s = date_now
        t = date_now
        u = '#반려동물카페, #애견카페, #애묘카페'
        insert = (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u)
        ws.append(insert)
        print(insert)
        # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
    wb.save('C:/workSpace/flask_crawling/originalDatas/A2221_반려동물_카페.xlsx')


if __name__ == '__main__':
    run()
