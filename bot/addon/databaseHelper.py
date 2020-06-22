import json
import sqlite3
import os

from .settingHelper import PROJECT_PATH, GROUP_SETTING_PATH, GROUP_LOG_PATH, CONFIG_LOG_PATH

class DBManager:
    default_group_setting = {
        "tweet": True,
        "retweet": True,
        "comment": True,
        "translation": True,
        "content": True,
        "no-report": False,
        "tag": f"{GROUP_SETTING_PATH}\\default_tag.png",
        "css-text": "font-family:黑体;font-size:25px;color:black"
    }

    def read_group_log(self, group_id: int, index: int) -> dict:
        if index < 0:
            return None
        db = sqlite3.connect(GROUP_LOG_PATH)
        db.execute(f"""CREATE TABLE IF NOT EXISTS "{group_id}" (
	                    "_ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                    "url"	TEXT,
	                    "code"	INTEGER
                    );""")
        db.commit()
        res = db.execute(f'SELECT * FROM "{group_id}" WHERE _ID = {index}').fetchone()
        db.close()
        if res is None:
            return None
        else:
            return {"url": res[1], "code": res[2]}

    def add_group_log(self, group_id: int, url: str, code: int) -> int:
        db = sqlite3.connect(GROUP_LOG_PATH)
        db.execute(f"""CREATE TABLE IF NOT EXISTS "{group_id}" (
	                    "_ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	                    "url"	TEXT,
	                    "code"	INTEGER
                    );""")
        maxIndex = db.execute(f'SELECT max(_ID) from "{group_id}";').fetchone()[0]
        if maxIndex is not None and maxIndex > 5000:
            prev = db.execute(f'SELECT * FROM "{group_id}";')
            db.execute(f'DELETE FROM "{group_id}"')
            prev = prev[round(len(prev) / 2):]
            db.executemany(f'INSERT INTO "{group_id}" VALUES (?, ?, ?)', prev)

        db.execute(f'INSERT INTO "{group_id}" VALUES (?, ?, ?)', (None, url, code))
        res = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.commit()
        db.close()
        return res

    def read_all_users(self) -> list:
        db = sqlite3.connect(CONFIG_LOG_PATH)
        res = db.execute('SELECT * FROM "users"').fetchall()
        result = [str(user[1]) for user in res]
        db.close()
        return result

    def read_specific_user(self, screen_name: str) -> list:
        db = sqlite3.connect(CONFIG_LOG_PATH)
        res = db.execute(f'SELECT * FROM "users" WHERE screen_name = "{screen_name}"').fetchone()
        db.close()
        if res is None:
            return None
        else:
            groups: list = [int(group) for group in res[2][:len(res[2]) - 1].split(",")]
            return groups

    def read_all_groups(self) -> list:
        db = sqlite3.connect(CONFIG_LOG_PATH)
        users: list = db.execute('SELECT * FROM "users"').fetchall()
        db.close()
        res = []
        for user in users:
            groups: list = [int(group) for group in user[2][:len(user[2]) - 1].split(",")]
            for group in groups:
                if group not in res:
                    res.append(group)
        return res

    def add_user(self, screen_name: str, user_id: str, group_id: int):
        db = sqlite3.connect(CONFIG_LOG_PATH)
        user_data: list = db.execute(f'SELECT * FROM "users" WHERE screen_name = "{screen_name}"').fetchone()
        append_group_id = str(group_id) + ","
        if user_data is None:
            user_data = (screen_name, user_id, append_group_id)
            db.execute('INSERT INTO "users" VALUES (?, ?, ?)', user_data)
        else:
            user_data = list(user_data)
            if user_data[2].find(append_group_id) == -1:
                user_data[2] = user_data[2] + append_group_id
                db.execute(f'UPDATE "users" SET groups = "{user_data[2]}" WHERE screen_name = "{screen_name}"')
        db.commit()
        db.close()

    def read_group_settings(self, group_id: int) -> dict:
        group_setting_file = f"{GROUP_SETTING_PATH}\\{group_id}.json"
        if os.path.exists(group_setting_file):
            with open(group_setting_file, "r", encoding="utf-8") as f:
                previous_setting = json.loads(f.read())
        else:
            previous_setting = self.default_group_setting.copy()
            with open(group_setting_file, "w", encoding="utf-8") as f:
                json.dump(previous_setting, f, ensure_ascii=False, indent=1)
        return previous_setting

    def adjust_group_settings(self, group_id: int, adjusted_value: dict):
        group_setting_file = f"{GROUP_SETTING_PATH}\\{group_id}.json"
        if os.path.exists(group_setting_file):
            with open(group_setting_file, "r", encoding="utf-8") as f:
                previous_setting = json.loads(f.read())
        else:
            previous_setting = self.default_group_setting.copy()
        for key in previous_setting.keys():
            if key in adjusted_value.keys():
                previous_setting[key] = adjusted_value[key]
        with open(group_setting_file, "w", encoding="utf-8") as f:
            json.dump(previous_setting, f, ensure_ascii=False, indent=1)
