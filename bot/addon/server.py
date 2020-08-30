import json
import random
import re
import urllib
import http
import hashlib

from requests_futures.sessions import FuturesSession

from .group_settings import GroupSetting
from .settings import SETTING

session = FuturesSession()


async def take_screenshot(url: str) -> dict:
    """
    向服务端发送截图请求
    :param url: 推文链接
    :return: 服务端截图结果
    """
    get = session.get(f"{SETTING.server_url}/screenshot",
                      json={"url": url}).result()
    return json.loads(get.content.decode("utf-8"))


async def add_translation(url: str, translation: str, group_setting: dict) -> dict:
    """
    向服务端发送嵌字请求
    :param url: 推文链接
    :param translation: 翻译文本
    :param group_setting: 群设置
    :return: 服务端嵌字结果
    """
    post_data = {
        "url": url,
        "translation": translation,
        "css-path": group_setting["css_path"],
        "tag-path": group_setting["tag_path"]
    }
    post = session.post(
        f"{SETTING.server_url}/translation", json=post_data).result()
    return json.loads(post.content.decode("utf-8"))


async def baidu_translation(content: str) -> str:
    """
    百度翻译
    :author: SoreHait ACE
    :param content: 翻译内容
    :return: 翻译结果
    """
    http_client = None
    myurl = '/api/trans/vip/translate'
    qaa = str(content)
    qaa = qaa.replace('\n', '')
    from_lang = 'auto'
    to_lang = 'zh'
    salt = random.randint(32768, 65536)
    sign = SETTING.baidu_api + qaa + str(salt) + SETTING.baidu_secret
    m1 = hashlib.md5()
    m2 = sign.encode(encoding='utf-8')
    m1.update(m2)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + SETTING.baidu_api + '&q=' + urllib.parse.quote(
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
