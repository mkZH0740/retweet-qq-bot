'''
@author: sudo, SoreHaitACE

'''
import requests, json, random, urllib, hashlib, re, http
# local server default port
SERVER_URL='http://127.0.0.1:8000'
#current directory
PROJECTPATH='C:\\Users\\Administrator\\Desktop\\3.3\\bot3.3\\'

__c_k__ = 'your twitter app custom key'
__c_s__ = 'your twitter custom secret'
__A_T__ = 'your twitter app access tooken'
__A_S__ = 'your twitter app access secret'
appid = 'baidu translation appid'
secretKey = 'baidu translation app secret'


def add_user(user_id:str,screen_name:str,group_id:int):
    d = {
        'user_id': user_id,
        'screen_name': screen_name
    }
    res = requests.post(f'{SERVER_URL}/adduser/{group_id}',json=d)
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return False
    return True


def read_all_users():
    res = requests.get(f'{SERVER_URL}/all')
    buf = json.loads(res.content.decode('utf-8'))
    for i in range(len(buf)):
        buf[i] = str(buf[i])
    return buf


def read_groups_of_user(screen_name:str):
    res = requests.get(f'{SERVER_URL}/readuser/{screen_name}')
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return None
    return buf# int!!!


def get_group_config(group_id:int):
    res = requests.get(f'{SERVER_URL}/rdb/{group_id}')
    return json.loads(res.content.decode('utf-8'))


def adj_group_config(adj_config:dict,group_id:int):
    res = requests.post(f'{SERVER_URL}/adb/{group_id}',json=adj_config)
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return False
    return True


def get_logged_tweet(index:int,group_id):
    res = requests.get(f'{SERVER_URL}/rldb/{group_id}/{index}')
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return None
    return buf


def add_translation(translation:str,url:str,tw_type:int,group_id:int):
    d = {
        'url': url,
        'tw_type': tw_type,
        'translation': translation,
        'group_id': group_id
    }
    res = requests.post(f'{SERVER_URL}/add_translation',json=d)
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return None
    return buf['filepath']


def generate_local_tweet_log(tweet:dict,tweet_id:str):
    with open(f'{PROJECTPATH}cache\\{tweet_id}.json','w',encoding='utf-8') as f:
        json.dump(tweet, f, indent=1, ensure_ascii=False)


def get_screenshot(url:str,tw_type:int):
    d = {
        'url': url,
        'tw_type': tw_type
    }
    res = requests.post(f'{SERVER_URL}/screenshot',json=d)
    buf = json.loads(res.content.decode('utf-8'))
    if 'status' in buf and not buf['status']:
        return None
    return buf


def add_to_group_log(url:str,tw_type:int,group_id:int):
    d = {
        'url': url,
        'tw_type': tw_type
    }
    res = requests.post(f'{SERVER_URL}/aldb/{group_id}',json=d)
    return int(json.loads(res.content.decode('utf-8'))['index'])


def trans(transstr: str):
    httpClient = None
    myurl = '/api/trans/vip/translate'
    qaa = str(transstr)
    qaa = qaa.replace('\n', '')
    fromLang = 'auto'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = str(appid) + qaa + str(salt) + str(secretKey)
    m1 = hashlib.md5()
    m2 = sign.encode(encoding='utf-8')
    m1.update(m2)
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
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
