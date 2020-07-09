import requests
import json
import hashlib
import urllib
import random
import re
import http

from .settingHelper import SERVER_URL, SCREENSHOT_PATH, BAIDU_API, BAIDU_SECRET


def takeScreenshot(url: str, code: int):
    data = {"url": url, "code": code}
    try:
        res = requests.post(url=f"{SERVER_URL}/screenshot", json=data)
        result = json.loads(res.content.decode('utf-8'))
        return result
    except Exception:
        return None


def addTranslation(url: str, code: int, translation: str, tag: str, style: str):
    data = {"url": url, "code": code, 
        "translation": translation, "tag": tag, "style": style}
    try:
        res = requests.post(url=f"{SERVER_URL}/translation", json=data)
        result = json.loads(res.content.decode('utf-8'))
        return result
    except Exception:
        return None


def baiduTranslation(content: str):
    httpClient = None
    myurl = '/api/trans/vip/translate'
    qaa = str(content)
    qaa = qaa.replace('\n', '')
    fromLang = 'auto'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = str(BAIDU_API) + qaa + str(salt) + str(BAIDU_SECRET)
    m1 = hashlib.md5()
    m2 = sign.encode(encoding='utf-8')
    m1.update(m2)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + BAIDU_API + '&q=' + urllib.parse.quote(
        qaa) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        resp = str(response.read())
        resu = str(re.findall('"dst":"(.+?)"', resp)[0])
        resul = resu.encode('utf-8').decode('unicode_escape')
        resultr = resul.encode('utf-8').decode('unicode_escape')
        result = resultr.replace(r'\/', r'/')
        return result
    except Exception as eb:
        return '翻译api超速，获取失败'
    finally:
        if httpClient:
            httpClient.close()