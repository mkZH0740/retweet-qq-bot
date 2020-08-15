import sqlite3
import json
import copy
import os

from .settings import CONFIG_DB, LOG_PATH, GROUP_SETTING_PATH, TAG_PATH, CSS_PATH
from typing import List

DEFAULT_GROUP_SETTINGS = {
    "tweet": True,
    "retweet": True,
    "comment": True,
    "original_text": True,
    "translate": True,
    "content": True,
    "tag_tath": f"{TAG_PATH}\\default_tag.png",
    "css_path": f"{CSS_PATH}\\default_text.css"
}

'''
SQLITE OPERATIONS
'''
def add_user(screen_name: str, twitter_id: str, group: str) -> bool:
    db = sqlite3.connect(CONFIG_DB)
    cursor = db.cursor()
    res = True
    previous_user = cursor.execute("SELECT * FROM 'users' WHERE twitter_id = ?", (twitter_id,)).fetchone()

    try:
        if previous_user is None:
            cursor.execute("INSERT INTO 'users' VALUES (?, ?, ?)", (screen_name, twitter_id, f"{group},"))
        else:
            cursor.execute("UPDATE 'users' SET groups = ? WHERE twitter_id = ?", (f"{previous_user[2]}{group},", twitter_id))
        db.commit()
    except Exception as e:
        print(e)
        res = False
    cursor.close()
    db.close()
    return res


def read_user_groups(twitter_id: str) -> List[str]:
    db = sqlite3.connect(CONFIG_DB)
    cursor = db.cursor()
    user = cursor.execute("SELECT * FROM 'users' WHERE twitter_id = ?", (twitter_id,)).fetchone()
    cursor.close()
    db.close()
    return [group for group in user[2].split(",") if group != ""]


def read_all_user_ids() -> List[str]:
    db = sqlite3.connect(CONFIG_DB)
    cursor = db.cursor()
    users = cursor.execute("SELECT * FROM 'users'").fetchall()
    cursor.close()
    db.close()
    return [str(user[1]) for user in users]


def read_all_groups() -> List[str]:
    db = sqlite3.connect(CONFIG_DB)
    cursor = db.cursor()
    users = cursor.execute("SELECT * FROM 'users'").fetchall()
    cursor.close()
    db.close()
    result = []
    for user in users:
        for group in user[2].split(","):
            if group != "" and group not in result:
                result.append(group)
    return result

'''
LOG OPERATIONS
'''
def add_group_log(group: str,  url: str) -> int:
    log_path = f"{LOG_PATH}\\{group}.txt"
    if not os.path.exists(log_path):
        open(log_path, "w", encoding="utf-8")
    with open(log_path, "r+", encoding="utf-8") as f:
        previous_content = f.readlines()
    previous_content.append(f"{url}\n")
    index = len(previous_content)
    if index > 5000:
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(previous_content[5000:])
            index -= 5000
    else:
        with open(log_path, "a+", encoding="utf-8") as f:
            f.write(previous_content.pop())
    return index

# throws exceptions! REAL INDEX!
def read_group_log(group: str, index: int) -> str:
    log_path = f"{LOG_PATH}\\{group}.txt"
    with open(log_path, "r", encoding="utf-8") as f:
        previous_content = f.readlines()
    if index < 0 or index > len(previous_content) - 1:
        raise RuntimeError("嵌字编号不合法！")
    return previous_content[index].strip()


def read_group_settings(group: str) -> dict:
    setting_path = f"{GROUP_SETTING_PATH}\\{group}.json"
    if os.path.exists(setting_path):
        with open(setting_path, "r", encoding="utf-8") as f:
            previous_settings = json.load(f)
    else:
        previous_settings = copy.deepcopy(DEFAULT_GROUP_SETTINGS)
        with open(setting_path, "w", encoding="utf-8") as f:
            json.dump(previous_settings, f, indent=1, ensure_ascii=False)
    return previous_settings


def add_group_settings(group: str, settings: dict):
    setting_path = f"{GROUP_SETTING_PATH}\\{group}.json"
    previous_settings = read_group_settings(group)
    for key, value in settings:
        if previous_settings.get(key) is not None:
            previous_settings[key] = value
    with open(setting_path, "w", encoding="utf-8") as f:
        json.dump(previous_settings, f, indent=1, ensure_ascii=False)
    