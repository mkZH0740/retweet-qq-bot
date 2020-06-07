import requests
import json
import sqlite3
import os
import random
import hashlib
import re
import urllib
import http

# 配置内容
ROOT_PATH = "C:\\Users\\Administrator\\Desktop\\proj4\\src\\bot\\"
GROUP_SETTING_PATH = "C:\\Users\\Administrator\\Desktop\\proj4\\src\\"
SERVER_ADDRESS = "http://127.0.0.1:8000/"
# twitter app的参数
__c_k__ = 'your custom key'
__c_s__ = 'your custom secret'
__A_T__ = 'your access token'
__A_S__ = 'your sccess secret'

# 百度翻译 app的参数
appid = 'your baidu translation appid'
secretKey = 'your baidu translation secret key'


def add_translation(data: dict):
    """
    :param data: 嵌字数据
    :return: 运行失败status和原因，或者截图名称
    """
    try:
        res = requests.post(url=f"{SERVER_ADDRESS}add_translation", json=data).content.decode("utf-8")
        return json.loads(res)
    except json.JSONDecodeError:
        return {"status": False, "reason": "服务器错误，无法完成该指令"}


def get_screenshot(data:dict):
    """
    :param data: 截图数据
    :return: 运行失败status和原因，或者截图名称和文本内容
    """
    try:
        res = requests.post(url=f"{SERVER_ADDRESS}get_screenshot", json=data).content.decode("utf-8")
        return json.loads(res)
    except json.JSONDecodeError:
        return {"status": False, "reason": "服务器错误，无法完成该指令"}


def read_group_settings(group_id: int) -> dict:
    """
    读取QQ群配置

    :param group_id: QQ群号
    :return: 配置
    """
    group_setting_file = f"{GROUP_SETTING_PATH}group_data\\{group_id}.json"
    # 默认配置
    default_group_setting = {
        "tweet": True,
        "retweet": True,
        "comment": True,
        "translation": True,
        "content": True,
        "no-report": False,
        "css-text": "font-family:黑体;font-size:28px;color:black"
    }
    if not os.path.exists(group_setting_file):
        # 该QQ群还没有配置，初始化默认配置
        with open(group_setting_file, "w", encoding="utf-8") as f:
            json.dump(default_group_setting, f, ensure_ascii=False, indent=1)
        return default_group_setting
    else:
        with open(group_setting_file, "r", encoding="utf-8") as f:
            res = json.load(f)
        return res


def adjust_group_settings(group_id: int, changed: dict):
    """
    编辑QQ群配置

    :param group_id: QQ群号
    :param changed: 被编辑的项目名称和值
    """
    group_setting_file = f"{GROUP_SETTING_PATH}group_data\\{group_id}.json"
    # 默认配置
    default_group_setting = {
        "tweet": True,
        "retweet": True,
        "comment": True,
        "translation": True,
        "content": True,
        "no-report": False,
        "css-text": "font-family:黑体;font-size:28px;color:black"
    }
    if not os.path.exists(group_setting_file):
        for key in changed.keys():
            if key in default_group_setting.keys():
                # 只编辑支持的配置项目
                default_group_setting[key] = changed[key]
        with open(group_setting_file, "w", encoding="utf-8") as f:
            json.dump(default_group_setting, f, ensure_ascii=False, indent=1)
    else:
        with open(group_setting_file, "r", encoding="utf-8") as f:
            previous: dict = json.load(f)
        for key in changed.keys():
            if key in previous.keys():
                previous[key] = changed[key]
        with open(group_setting_file, "w", encoding="utf-8") as f:
            json.dump(previous, f, ensure_ascii=False, indent=1)


class DatabaseProcessor:
    """
    数据处理类，包装了一些数据文件处理的方法，主要是sqlite数据库的处理方法
    """
    # 两个数据库的路径
    group_log_db = f"{ROOT_PATH}bin\\logs.db"
    config_log_db = f"{ROOT_PATH}bin\\configs.db"

    def read_group_log(self, group_id: int, index: int):
        """
        读取QQ群log

        :param group_id: QQ群号
        :param index: 过往推特的嵌字编号
        :return: 过往推特内容或者None
        """
        db = sqlite3.connect(self.group_log_db)
        # 如果该组的表还不存在就创建一下
        db.execute(f'CREATE TABLE IF NOT EXISTS "{group_id}" ("url" String, "tw_type" INTEGER)')
        db.commit()
        res = db.execute(f'SELECT * FROM "{group_id}"').fetchall()
        if index < len(res):
            db.close()
            # [url, tw_type]
            return res[index]
        else:
            db.close()
            return None

    def add_group_log(self, group_id: int, url: str, tw_type: int):
        """
        加入QQ群log

        :param group_id: QQ群号
        :param url: tweet URL
        :param tw_type: tweet类型代码
        :return: 嵌字编号
        """
        db = sqlite3.connect(self.group_log_db)
        db.execute(f'CREATE TABLE IF NOT EXISTS "{group_id}" ("url" String, "tw_type" INTEGER)')
        prev = db.execute(f'SELECT * FROM "{group_id}"').fetchall()
        if len(prev) > 3000:
            # 太多了，清理一下
            prev = prev[round(len(prev))/2:]
            db.execute(f'DELETE FROM "{group_id}"')
            db.executemany(f'INSERT INTO "{group_id}" VALUES (?, ?)', prev)

        db.execute(f'INSERT INTO "{group_id}" VALUES (?, ?)', (url, tw_type))
        res = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.commit()
        db.close()
        return res

    def read_user(self, screen_name: str) -> list:
        """
        读取监听用户的QQ群

        :param screen_name: 推特用户的screen_name
        :return: QQ群号的列表
        """
        db = sqlite3.connect(self.config_log_db)
        res = db.execute(f'SELECT * FROM "users" WHERE screen_name = "{screen_name}"').fetchone()
        db.close()
        if len(res) == 0:
            # 该用户不存在
            return None
        else:
            # [screen_name, user_id, groups]
            groups: list = res[2].split(",")
            groups.pop()
            for i in range(len(groups)):
                groups[i] = int(groups[i])
            return groups

    def read_all_users(self):
        """
        读取所用用户

        :return: 所有用户的列表
        """
        db = sqlite3.connect(self.config_log_db)
        res = db.execute('SELECT * FROM "users"').fetchall()
        db.close()
        return res

    def read_all_groups(self):
        """
        读取所有正在监听对象的QQ群号

        :return:
        """
        users = self.read_all_users()
        res = []
        for user in users:
            groups = user[2].split(",")
            groups.pop()
            for i in range(len(groups)):
                if int(groups[i]) not in res:
                    # 消除所有重复的QQ群号
                    res.append(int(groups[i]))
        return res

    def add_user(self, screen_name: str, user_id: str, group_id: int):
        """
        加入新用户

        :param screen_name: 用户的screen name
        :param user_id: 用户的id
        :param group_id: QQ群的群号
        """
        db = sqlite3.connect(self.config_log_db)
        user_data: list = db.execute(f'SELECT * FROM "users" WHERE screen_name = "{screen_name}"').fetchone()
        if user_data is None:
            user_data = [screen_name, user_id, str(group_id) + ","]
            db.execute(f'INSERT INTO "users" VALUES {tuple(user_data)}')
        else:
            user_data = list(user_data)
            if user_data[2].find(str(group_id)) == -1:
                # 该QQ群尚未监听该用户
                user_data[2] = user_data[2] + str(group_id) + ","
                db.execute(f'UPDATE "users" SET groups = "{user_data[2]}" WHERE screen_name = "{screen_name}"')
        db.commit()
        db.close()


def trans(transstr: str):
    """
    翻译原文
    @author: SoreHait

    :param transstr: 待翻译的文本
    :return: 翻译好的文本
    """
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
