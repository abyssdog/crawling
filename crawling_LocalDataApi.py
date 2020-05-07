# -- coding: utf-8 --
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
from openpyxl import Workbook
import datetime
import json


def save():
    url = 'http://www.localdata.kr/platform/rest/GR0/openDataApi?authKey=NgFWarT7H1FOSAcIhU8MDlOqA9xf/n74DomUkJKJJEw='
    queryParams = '&' + urlencode(
        {
            quote_plus('pageSize'): 100,
            quote_plus('resultType'): 'json'
        }
    )
    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read().decode('utf-8')
    info = json.loads(response_body)

    now = datetime.datetime.now()
    date_now = datetime.datetime.strftime(now, "%Y-%m-%d")
    wb = Workbook()
    ws = wb.active
    # 첫행 입력
    ws.append(('번호', '개방서비스명', '개방서비스ID', '개방자치단체코드', '관리번호', '인허가일자', '인허가취소일자', '영업상태구분코드',
               '영업상태명', '상세영업상태코드', '상세영업상태명', '폐업일자', '휴업시작일자', '휴업종료일자', '재개업일자',
               '소재지전화', '소재지면적', '소재지우편번호', '소재지전체주소', '도로명전체주소', '도로명우편번호', '사업장명',
               '최종수정시점', '데이터갱신구분', '데이터갱신일자', '업태구분명', '좌표정보(X)', '좌표정보(Y)'))
    # DB 모든 데이터 엑셀로
    cnt = 0
    for item in info['result']['body']['rows'][0]['row']:
        a = item['rowNum']
        b = item['opnSvcNm']
        c = item['opnSvcId']
        d = item['opnSfTeamCode']
        e = str(item['mgtNo'])
        f = item['apvPermYmd']
        g = item['apvCancelYmd']
        h = item['trdStateGbn']
        i = item['trdStateNm']
        j = item['dtlStateGbn']
        k = item['dtlStateNm']
        l = item['dcbYmd']
        m = item['clgStdt']
        n = item['clgEnddt']
        o = item['ropnYmd']
        p = item['siteTel']
        q = item['siteArea']
        r = item['sitePostNo']
        s = item['siteWhlAddr']
        t = item['rdnWhlAddr']
        u = item['rdnPostNo']
        v = item['bplcNm']
        w = str(item['lastModTs'])
        x = item['updateGbn']
        y = item['updateDt']
        z = item['uptaeNm']
        aa = item['x']
        ab = item['y']
        # item['updateGbn'] => U : 갱신, I : 신규 데이터
        if x == 'I':
            insert = (a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, aa, ab)
            ws.append(insert)
            print(insert)
        else:
            print('여기다가 db 데이터 불러와서 갱신된 데이터 Update 하는거 만들면 될듯.')

    wb.save('C:/workSpace/flask_crawling/originalDatas/동물병원.xlsx')


if __name__ == '__main__':
    save()
