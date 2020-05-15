# -- coding: utf-8 --
import requests
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote

url = 'http://api.data.go.kr/openapi/tn_pubr_public_pblprfr_event_info_api'
queryParams = '?' + urlencode(
    {
        quote_plus('ServiceKey'): 'jcL0viqxp%2BIpqo2XNQM6qAI%2Bbw5HbnhgWorBckylzA81UC1d48rhhZdWMjMxwvb2slqTgmZpxaC27zWjn83nrQ%3D%3D'
    }
)

request = Request(url + queryParams)
request.get_method = lambda: 'GET'
response_body = urlopen(request).read()
print(response_body)