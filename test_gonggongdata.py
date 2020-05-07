# -- coding: utf-8 --
import requests
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote

API_Key = unquote('jcL0viqxp+Ipqo2XNQM6qAI+bw5HbnhgWorBckylzA81UC1d48rhhZdWMjMxwvb2slqTgmZpxaC27zWjn83nrQ==')
_API_Key = 'jcL0viqxp%2BIpqo2XNQM6qAI%2Bbw5HbnhgWorBckylzA81UC1d48rhhZdWMjMxwvb2slqTgmZpxaC27zWjn83nrQ%3D%3D'

url = 'http://openapi.animal.go.kr/openapi/service/rest/animalShelterSrvc/shelterInfo'
queryParams = '?' + urlencode(
    {
        quote_plus('care_reg_no'): '326999201900001',
        quote_plus('care_nm'): '유기동물 테스트시설',
        quote_plus('serviceKey'): _API_Key,
     }
)
request = Request(url+queryParams)
request.get_method = lambda: 'GET'
response_body = urlopen(request).read().decode('utf-8')

print(response_body)
