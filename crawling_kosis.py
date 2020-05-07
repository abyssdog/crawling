import requests
import pandas as pd
from pandas.io.json import json_normalize
import sqlite3
from simplejson import JSONDecodeError
import time


def kosis(s_year, e_year, url_one):
    one_year = url_one.split('startPrdDe=')[1][:4]
    year_want = list(range(s_year, e_year + 1))
    result = pd.DataFrame()
    for year in year_want:
        try:
            url = url_one.split(str(one_year))[0] + str(year) + url_one.split(str(one_year))[1] + str(year) + url_one.split(str(one_year))[2]
            print(url)
            r = requests.get(url)
            data = r.json()
            df = pd.DataFrame.from_dict(json_normalize(data), orient='columns')
            result = result.append(df)
            time.sleep(1)
        except JSONDecodeError:
            print("{0}년 마지막 페이지에 도달했습니다.".format(year))
            break

    return result

da01 = kosis(2005, 2017, 'http://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey=apiKey&itmId=T1+&objL1=ALL&objL2=ALL&objL3=&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=Y&startPrdDe=2017&endPrdDe=2017&loadGubun=2&orgId=210&tblId=DT_21002_P011')