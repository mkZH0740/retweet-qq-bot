import requests
import json
import random
import hashlib
import http
import urllib
import re

from .settings import SERVER_URL, BAIDU_API, BAIDU_SECRET

def add_translation(url: str, translation: str, group_settings: dict):
    result = json.loads(requests.post(f"{SERVER_URL}/translate", json={
                "url": url,
                "translation": translation,
                "tagPath": group_settings["tag_path"],
                "cssPath": group_settings["css_path"]
            }).content.decode("utf-8"))
    return result

def take_screenshot(url: str):
    result = json.loads(requests.post(f"{SERVER_URL}/screenshot", json={
                "url": url
            }).content.decode("utf-8"))
    return result

async def baidu_translation(content: str):
    http_client = None
    myurl = '/api/trans/vip/translate'
    qaa = str(content)
    qaa = qaa.replace('\n', '')
    from_lang = 'auto'
    to_lang = 'zh'
    salt = random.randint(32768, 65536)
    sign = str(BAIDU_API) + qaa + str(salt) + str(BAIDU_SECRET)
    m1 = hashlib.md5()
    m2 = sign.encode(encoding='utf-8')
    m1.update(m2)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + BAIDU_API + '&q=' + urllib.parse.quote(
        qaa) + '&from=' + from_lang + '&to=' + to_lang + '&salt=' + str(salt) + '&sign=' + sign
    try:
        http_client = http.client.HTTPConnection('api.fanyi.baidu.com')
        http_client.request('GET', myurl)
        response = http_client.getresponse()
        resp = str(response.read())
        resu = str(re.findall('"dst":"(.+?)"', resp)[0])
        resul = resu.encode('utf-8').decode('unicode_escape')
        resultr = resul.encode('utf-8').decode('unicode_escape')
        result = resultr.replace(r'\/', r'/')
        return result
    except Exception:
        return '翻译api超速，获取失败'
    finally:
        if http_client:
            http_client.close()