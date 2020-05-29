from urllib.parse import urlencode, quote_plus
from urllib.request import Request, urlopen

url = 'http://api.data.go.kr/openapi/tn_pubr_public_pblprfr_event_info_api'
queryParams = '?' + urlencode(
    {
        quote_plus('ServiceKey'): 'jcL0viqxp%2BIpqo2XNQM6qAI%2Bbw5HbnhgWorBckylzA81UC'
                                  '1d48rhhZdWMjMxwvb2slqTgmZpxaC27zWjn83nrQ%3D%3D',
        quote_plus('pageNo'): '1',
        quote_plus('numOfRows'): '100',
        quote_plus('type'): 'xml',
        quote_plus('eventNm'): '도민체전 성공기원을 위한 음악회',
        quote_plus('opar'): '서천문예의 전당 대강당',
        quote_plus('eventCo'): '제71회 충남도민체전 성공 개최를 기원하는 음악회',
        quote_plus('eventStartDate'): '2019-04-25',
        quote_plus('eventEndDate'): '2019-04-25',
        quote_plus('eventTime'): '19:00',
        quote_plus('chrgeInfo'): '무료',
        quote_plus('mnnst'): '서천군',
        quote_plus('auspcInstt'): '서천군',
        quote_plus('phoneNumber'): '',
        quote_plus('suprtInstt'): '',
        quote_plus('seatNumber'): '',
        quote_plus('admfee'): '',
        quote_plus('entncAge'): '',
        quote_plus('dscntInfo'): '',
        quote_plus('atpn'): '',
        quote_plus('homepageUrl'): '',
        quote_plus('advantkInfo'): '',
        quote_plus('prkplceYn'): 'Y',
        quote_plus('rdnmadr'): '충청남도 서천군 서천읍 서천로14번길 20',
        quote_plus('lnmadr'): '충청남도 서천군 서천읍 군사리 176-2',
        quote_plus('latitude'): '36.0763774',
        quote_plus('hardness'): '126.6983685',
        quote_plus('referenceDate'): '2019-12-31',
        quote_plus('insttCode'): '4580000',
        quote_plus('insttNm'): ''
    }
)

request = Request(url + queryParams)
request.get_method = lambda: 'GET'
response_body = urlopen(request).read()
print(response_body)
