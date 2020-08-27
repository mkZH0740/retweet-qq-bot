import sqlite3
import json

from typing import List, Dict

from .settings import SETTING


class User:
    screen_name: str
    user_id: str
    groups: List[str] = []

    def __init__(self, screen_name: str, user_id: str):
        self.screen_name = screen_name
        self.user_id = user_id

    def add_group(self, group_id: str):
        if group_id not in self.groups:
            self.groups.append(group_id)

    def load_group(self, raw: str):
        self.groups = raw.split(",")
        self.groups.pop()
        for i, group in enumerate(self.groups):
            self.groups[i] = str(group)

    def _generate_whole_value(self):
        return (self.screen_name, self.user_id, ",".join(self.groups) + ",")

    def _generate_group_value(self) -> tuple:
        return (",".join(self.groups) + ",", self.screen_name)


class Database:
    users: Dict[str, User] = {}

    def __init__(self):
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        raw_db_data = cursor.execute("SELECT * FROM 'users'").fetchall()
        for user in raw_db_data:
            curr_user = User(user[0], str(user[1]))
            curr_user.load_group(user[2])
            self.users[curr_user.screen_name] = curr_user

        cursor.close()
        db.close()

        if SETTING.debug:
            print("@ Database LOADED")

    def get_user(self, screen_name: str) -> User:
        return self.users.get(screen_name, None)

    def get_user_id(self, user_id: str) -> User:
        for user in self.users.values():
            if user.user_id == user_id:
                return user
        return None

    def delete_user(self, screen_name: str, group_id: str):
        previous_user = self.get_user(screen_name)
        try:
            previous_user.groups.remove(group_id)
        except ValueError:
            return
        if len(previous_user.groups) == 0:
            self._delete_user(previous_user)
        else:
            self._update_previous_user(previous_user)

    def add_user(self, screen_name: str, user_id: str, group_id: str):
        previous_user = self.get_user(screen_name)
        if previous_user is None:
            curr_user = User(screen_name, user_id)
            curr_user.add_group(group_id)
            self.users[screen_name] = curr_user
            self._update_new_user(curr_user)
        else:
            previous_user.add_group(group_id)
            self._update_previous_user(previous_user)

    def read_all_groups(self) -> List[str]:
        result_groups: List[str] = []
        for user in self.users.values():
            for group in user.groups:
                if group not in result_groups:
                    result_groups.append(group)
        return result_groups

    def read_all_user_ids(self) -> List[str]:
        result_ids: List[str] = []
        for user in self.users.values():
            result_ids.append(str(user.user_id))
        return result_ids

    def _update_new_user(self, new_user: User):
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute("INSERT INTO 'users' VALUES (?, ?, ?)",
                       new_user._generate_whole_value())
        db.commit()
        cursor.close()
        db.close()

    def _update_previous_user(self, new_user: User):
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute("UPDATE 'users' SET groups = ? WHERE screen_name = ?",
                       new_user._generate_group_value())
        db.commit()
        cursor.close()
        db.close()

    def _delete_user(self, user: User):
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM 'users' WHERE screen_name = ?", (user.screen_name,))
        db.commit()
        cursor.close()
        db.close()


databse = Database()
