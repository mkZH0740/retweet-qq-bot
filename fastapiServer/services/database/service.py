from fastapi import APIRouter
from services.config import ROOTPATH
from pydantic import BaseModel
import os, json, sqlite3

USERDBPATH = f'{ROOTPATH}bin\\config.db'
LOGDBPATH = f'{ROOTPATH}bin\\logs.db'
router = APIRouter()


class GroupConfig(BaseModel):
    tweet: bool = None
    retweet: bool = None
    comment: bool = None
    translation: bool = None
    content: bool = None
    styles: str = None


@router.post('/adb/{group_id}')
def adj_group_config(group_id:str, new_config:GroupConfig):
    config_path = f'{ROOTPATH}configs\\{group_id}.json'
    buf = new_config.dict()
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            for k in buf.keys():
                if buf[k] is None:
                    buf[k] = True
                buf['styles'] = "font-size:25px; font-family:'黑体'"
            json.dump(buf, f, indent=1, ensure_ascii=False)
        return {'status':True}
    with open(config_path, 'r', encoding='utf-8') as f:
        present_config = json.load(f)
    for k in buf.keys():
        if buf[k] is not None:
            present_config[k] = buf[k]
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(present_config, f, indent=1, ensure_ascii=False)
    return {'status':True}


@router.get('/rdb/{group_id}')
def get_group_config(group_id:str):
    config_path = f'{ROOTPATH}configs\\{group_id}.json'
    if not os.path.exists(config_path):
        with open(config_path, 'w', encoding='utf-8') as f:
            default_config = {
                'tweet': True,
                'retweet': True,
                'comment': True,
                'translation': True,
                'content': True,
                'styles': "font-size:25px; font-family:'黑体'"
            }
            json.dump(default_config, f, indent=1, ensure_ascii=False)
        return default_config
    with open(config_path, 'r', encoding='utf-8') as f:
        buf = json.load(f)
    return buf


@router.get('/all')
def get_all_users_id():
    user_db = sqlite3.connect(USERDBPATH)
    users = []
    cursor = user_db.cursor()
    cursor.execute('SELECT * FROM "users"')
    buf = cursor.fetchall()
    cursor.close()
    user_db.close()
    for d in buf:
        users.append(d[0])
    return users


class TweetUser(BaseModel):
    user_id:int
    screen_name:str


@router.post('/adduser/{group_id}')
def add_user(group_id:int, user:TweetUser):
    user_db = sqlite3.connect(USERDBPATH)
    cursor = user_db.cursor()
    cursor.execute('SELECT * FROM "users" WHERE user_id = ?', [user.user_id])
    buf = cursor.fetchone()
    if buf is None:
        cursor.execute('INSERT INTO "users"(user_id, screen_name, groups) VALUES (?, ?, ?)', [user.user_id, user.screen_name, str([group_id])])
    else:
        present_groups: list = json.loads(buf[2])
        if group_id in present_groups:
            cursor.close()
            user_db.close()
            return {'status':False}
        present_groups.append(group_id)
        cursor.execute('UPDATE "users" SET groups = ? WHERE screen_name = ?', [str(present_groups), user.screen_name])
    user_db.commit()
    cursor.close()
    user_db.close()
    return {'status':True}


@router.get('/readuser/{screen_name}')
def get_group(screen_name:str):
    user_db = sqlite3.connect(USERDBPATH)
    cursor = user_db.cursor()
    cursor.execute('SELECT * FROM "users" WHERE screen_name = ?', [screen_name])
    buf = cursor.fetchone()
    if buf is None:
        cursor.close()
        user_db.close()
        return {'status':False}
    return json.loads(buf[2])


@router.get('/rldb/{group_id}/{index}')
def get_logged_tweet(group_id:str,index:int):
    log_db = sqlite3.connect(LOGDBPATH)
    cursor = log_db.cursor()
    cursor.execute(f'SELECT * FROM "{group_id}" WHERE id={index}')
    res = cursor.fetchone()
    if res is None:
        cursor.close()
        log_db.close()
        return {'status':False}
    return {'url':res[1], 'tw_type':res[2]}


class GroupLogTweet(BaseModel):
    url:str
    tw_type:int


@router.post('/aldb/{group_id}')
def add_log_tweet(group_id:str, grouplogtweet:GroupLogTweet):
    log_db = sqlite3.connect(LOGDBPATH)
    cursor = log_db.cursor()
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{group_id}" (id INTEGER NOT NULL,url String, tw_type INTEGER, PRIMARY KEY (id))')
    cursor.execute(f'INSERT INTO "{group_id}" (id, url, tw_type) VALUES (NULL,?,?)', [grouplogtweet.url, grouplogtweet.tw_type])
    cursor.execute('SELECT last_insert_rowid()')
    index = str(cursor.fetchone()[0])
    log_db.commit()
    cursor.close()
    log_db.close()
    return {'index': index}
