# -- coding: utf-8 --
import requests
from bs4 import BeautifulSoup as Bs
import xml.etree.ElementTree as ET


def api(keyword):
    api_key = '086999c8ccb0ef6b4acfd882c8197149'
    # keyword = '반려견'
    #url = 'http://openapi.11st.co.kr/openapi/OpenApiService.tmall?key={key}&apiCode= ProductSearch&keyword ={keyword}'
    url = 'http://openapi.11st.co.kr/openapi/OpenApiService.tmall?key='+api_key+'&apiCode=ProductSearch&keyword='+keyword
    response = requests.get(url.format(key=api_key, keyword=keyword))
    processing = True
    while processing:
        text = response.text
        root = ET.fromstring(response.text)
        for strTag in root.iter('str'):
            if strTag.attrib.get('name')=='status' :
                processing = False


if __name__ == '__main__':
    # api('dog')
    t = [1, 5, 7, 33, 39, 52]
    for p in enumerate(t):
        print(p)