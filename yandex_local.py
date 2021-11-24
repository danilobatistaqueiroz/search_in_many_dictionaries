import requests
import json
import traceback
import os

def get_data(text):
    api_url = 'https://translate.yandex.net/api/v1/tr.json/translate?id=f7e8cfec.60ad709a.33e64937.74722d74657874-2-0&srv=tr-text&lang=en-pt&reason=auto&format=text&yu=5691578261621979255&yum=1621979258968172770'
    request_data = requests.post(api_url, data={"text":text})
    j = request_data.json()
    if "text" in j:
        return j['text'][0]
    else:
        return ''

#print(get_data('hello, hi'))