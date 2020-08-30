import sqlite3
import json

from typing import List, Dict

from .settings import SETTING


class User:
    """
    此类包装了推特用户
    """
    screen_name: str
    user_id: str
    groups: List[str] = []

    def __init__(self, screen_name: str, user_id: str):
        self.screen_name = screen_name
        self.user_id = user_id

    def add_group(self, group_id: str):
        """
        为推特用户加入新群
        """
        if group_id not in self.groups:
            self.groups.append(group_id)

    def load_group(self, raw: str):
        """
        依照sqlite数据库中的条目读取所有群
        """
        self.groups = raw.split(",")
        # sqlite中条目以","结尾，清除结尾的空字符
        self.groups.pop()
        for i, group in enumerate(self.groups):
            self.groups[i] = str(group)

    def _generate_whole_value(self):
        """
        生成tuple
        """
        return (self.screen_name, self.user_id, ",".join(self.groups) + ",")

    def _generate_group_value(self) -> tuple:
        """
        生成群号tuple
        """
        return (",".join(self.groups) + ",", self.screen_name)


class Database:
    """
    此类保存所有的推特用户
    """
    # 用字典保存所有推特用户
    users: Dict[str, User] = {}

    def __init__(self):
        """
        从sqlite数据库中读取所有推特用户
        """
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        raw_db_data = cursor.execute("SELECT * FROM 'users'").fetchall()
        for user in raw_db_data:
            # screen_name, twitter_id, groups
            curr_user = User(user[0], str(user[1]))
            curr_user.load_group(user[2])
            self.users[curr_user.screen_name] = curr_user

        cursor.close()
        db.close()

        if SETTING.debug:
            print("@ Database LOADED")

    def get_user(self, screen_name: str) -> User:
        """
        根据screen name读取用户
        :param screen_name: 推特用户的screen_name
        :return: 用户对象
        """
        return self.users.get(screen_name, None)

    def get_user_id(self, user_id: str) -> User:
        """
        根据user id读取用户
        :param user_id: 推特用户的user id
        :return: 用户对象
        """
        for user in self.users.values():
            if user.user_id == user_id:
                return user
        return None

    def delete_user(self, screen_name: str, group_id: str):
        """
        删除用户
        :param screen_name: 推特用户的screen_name
        :param group_id: 群号
        """
        previous_user = self.get_user(screen_name)
        try:
            previous_user.groups.remove(group_id)
        except ValueError:
            # 群号不存在
            return
        if len(previous_user.groups) == 0:
            # 已经不存在监听该用户的群，删除该用户
            self._delete_user(previous_user)
        else:
            # 移除群
            self._update_previous_user(previous_user)

    def add_user(self, screen_name: str, user_id: str, group_id: str):
        """
        增加用户
        :param screen_name: 推特用户的screen_name
        :param user_id: 推特用户的user id
        :param group_id: 群号
        """
        previous_user = self.get_user(screen_name)
        if previous_user is None:
            # 该用户不存在，初始化该用户
            curr_user = User(screen_name, user_id)
            curr_user.add_group(group_id)
            self.users[screen_name] = curr_user
            self._update_new_user(curr_user)
        else:
            # 该用户已存在，更新groups
            previous_user.add_group(group_id)
            self._update_previous_user(previous_user)

    def read_all_groups(self) -> List[str]:
        """
        读取所有存在监听用户的群
        :return: 所有存在监听用户的群
        """
        result_groups: List[str] = []
        for user in self.users.values():
            for group in user.groups:
                if group not in result_groups:
                    result_groups.append(group)
        return result_groups

    def read_all_user_ids(self) -> List[str]:
        """
        读取所有用户的推特id
        :return: 所有用户的推特id
        """
        result_ids: List[str] = []
        for user in self.users.values():
            result_ids.append(str(user.user_id))
        return result_ids

    def _update_new_user(self, new_user: User):
        """
        更新sqlite数据库，加入新用户
        :param new_user: 用户对象
        """
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute("INSERT INTO 'users' VALUES (?, ?, ?)",
                       new_user._generate_whole_value())
        db.commit()
        cursor.close()
        db.close()

    def _update_previous_user(self, new_user: User):
        """
        更新sqlite数据库，更新已存在的用户
        :param new_user: 用户对象
        """
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute("UPDATE 'users' SET groups = ? WHERE screen_name = ?",
                       new_user._generate_group_value())
        db.commit()
        cursor.close()
        db.close()

    def _delete_user(self, user: User):
        """
        更新sqlite数据库，删除已存在的用户
        :param user: 用户对象
        """
        db = sqlite3.connect(SETTING.config_path)
        cursor = db.cursor()

        cursor.execute(
            "DELETE FROM 'users' WHERE screen_name = ?", (user.screen_name,))
        db.commit()
        cursor.close()
        db.close()


# 全局用户代理
databse = Database()
