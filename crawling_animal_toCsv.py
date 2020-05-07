import csv
import datetime
import re
import time

import pymysql
from bs4 import BeautifulSoup
import requests
from openpyxl import Workbook


def run():
    category = ['protection', 'agent', 'hospital', 'production', 'importation', 'sales',
                'exhibition', 'management', 'transportation', 'beauty', 'funeral']
    res = []
    page = {
        'protection': 30, 'agent': 356, 'hospital': 482, 'production': 178,
        'importation': 8, 'sales': 420, 'exhibition': 61,
        'management': 408, 'transportation': 52, 'beauty': 672, 'funeral': 5
    }
    url = {
        'protection': 'https://www.animal.go.kr/front/awtis/institution/institutionList.do?totalCount=293&pageSize=10&menuNo=1000000059&&page={}',
        'agent': 'https://www.animal.go.kr/front/awtis/record/recordAgencyList.do?totalCount=3556&pageSize=10&menuNo=2000000002&&page={}',
        'hospital': 'https://www.animal.go.kr/front/awtis/shop/hospitalList.do?totalCount=4811&pageSize=10&menuNo=6000000002&&page={}',
        'production': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=1776&pageSize=10&sWrkCd=C&menuNo=6000000004&&page={}',
        'importation': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=79&pageSize=10&sWrkCd=B&menuNo=6000000005&&page={}',
        'sales': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=4197&pageSize=10&sWrkCd=A&menuNo=6000000009&&page={}',
        'exhibition': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=603&pageSize=10&sWrkCd=D&menuNo=6000000010&&page={}',
        'management': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=4080&pageSize=10&sWrkCd=E&menuNo=6000000128&&page={}',
        'transportation': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=512&pageSize=10&sWrkCd=G&menuNo=6000000129&&page={}',
        'beauty': 'https://www.animal.go.kr/front/awtis/shop/salesList.do?totalCount=6711&pageSize=10&sWrkCd=F&menuNo=6000000130&&page={}',
        'funeral': 'https://www.animal.go.kr/front/awtis/shop/undertaker1List.do?totalCount=44&pageSize=10&menuNo=6000000131&&page={}'
    }
    temp = category[0]
    for page in range(1, page[temp]+1):
        time.sleep(2)
        response = requests.get(url[temp].format(page))
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        trs = table.find_all_next('tr')
        cnt = 0
        for idx, tr in enumerate(trs):
            if idx > 0:
                arr = {}
                cnt += 1
                tds = tr.find_all('td')
                # agent
                '''arr['company'] = tds[0].text.strip()  # 회사 이름
                arr['ceo'] = tds[1].text.strip()  # 사장 이름 : 병원은 없음
                arr['phone'] = tds[2].text.strip()  # 전화 번호
                arr['address'] = tds[3].text.strip()  # 회사 주소'''
                # hospital
                '''arr['company'] = tds[1].text.strip()  # 회사 이름
                arr['ceo'] = '-'  # 사장 이름 : 병원은 없음
                arr['phone'] = tds[2].text.strip()  # 전화 번호
                arr['address'] = tds[3].text.strip()  # 회사 주소
                arr['home_page'] = "-"'''
                # production, importation, sales
                '''arr['company'] = tds[2].text.strip()  # 회사 이름
                arr['ceo'] = '-'  # 사장 이름 : 병원은 없음
                arr['phone'] = tds[3].text.strip()  # 전화 번호
                arr['address'] = tds[4].text.strip()  # 회사 주소
                arr['home_page'] = "-"  # 홈페이지'''
                # protection
                arr['company'] = tds[1].text.strip()  # 회사 이름
                arr['ceo'] = '-'  # 사장 이름 : 병원은 없음
                arr['phone'] = tds[2].text.strip()  # 전화 번호
                arr['address'] = tds[3].text.strip()  # 회사 주소
                arr['home_page'] = "-"  # 홈페이지
                # puneral
                '''arr['company'] = tds[1].text.strip()  # 회사 이름
                arr['ceo'] = '-'  # 사장 이름 : 병원은 없음
                arr['phone'] = tds[2].text.strip()  # 전화 번호
                arr['address'] = tds[3].text.strip()  # 회사 주소
                arr['home_page'] = tds[5].text.strip()  # 회사 주소'''
                #content_insert(arr, temp)
                res.append(arr)
                print('{}{}{}{}{}'.format(cnt, arr['company'], arr['ceo'], arr['phone'], arr['address']))
    save(res, temp)


def save(arr, keyword):
    now = datetime.datetime.now()
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
    file_count = 1
    wb = Workbook()
    ws = wb.active
    # 첫행 입력
    ws.append(('ID', '데이터 분류명', '기관/회사명', '주요내용 및 서비스', '메모 및 기타', '기준년월일', '경과기간(개월)',
               '출처', '데이터 생성자', '데이터 저작권', '데이터 수집방법', '데이터 프로토콜', '데이터 소스', '데이터 저장소',
               '데이터 확장 방법', '데이터 확장 참조', '등록자', '수정자', '등록일', '수정일', '키워드'))
    # DB 모든 데이터 엑셀로
    cnt = 0
    for row in arr:
        cnt += 1
        temp_str = row['address']
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
        a = 'A3113_' + str(cnt).rjust(4, '0')  # ok
        b = row['company']  # 여기에 업체명
        c = c_var  # 여기에는 지역 대구분 ex) 시, 도
        d = d_var  # 여기는 지역 소구분 ex) 구 동
        if row['phone'] == '-':
            e = '-'
        else:
            e = row['phone']
        f = date_now
        g = '0'
        h = '동물보호관리시스템'
        i = '재사용'
        j = '공개'
        k = '크롤링'
        l = 'http'
        m = 'https://www.animal.go.kr/front/awtis/institution/institutionList.do?menuNo=1000000059'
        n = 'www'
        o = '1'
        p = 'c'
        q = '이준재'
        r = '이준재'
        s = date_now
        t = date_now
        u = '#동물보호센터'
        insert = (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u)
        ws.append(insert)
        print(insert)
        # row[1] : 업체명, row[2] : 대표명, row[3] : 전화번호, row[4] : 주소
    wb.save('C:/workSpace/flask_crawling/originalDatas/A3113_반려동물_보호센터.xlsx')


if __name__ == '__main__':
    run()
