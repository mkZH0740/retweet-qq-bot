from tweepy import StreamListener
from .databaseHelper import DBManager
from .settingHelper import TWEET_LOG_PATH
from .serverHelper import takeScreenshot

import json
import os


class MyListener(StreamListener):
    manager = DBManager()
    errList = []
    followedUsers = []

    
    def __init__(self, api=None):
        self.followedUsers = self.manager.read_all_users()
        print(self.followedUsers)
        super().__init__(api=api)
    

    def _generate_valid_result(self):
        return {
            "url": "",
            "code": 1,
            "screenshotPath": None,
            "rawText": "",
            "mediaUrls": [],
            "groups": {}
        }
    

    def regenerate_followed_users(self):
        self.followedUsers = self.manager.read_all_users()
        print(self.followedUsers)

    def on_status(self, status):
        if status.user.id_str not in self.followedUsers:
            return
        screenName: str = status.user.screen_name
        tweetId: str = status.id_str

        validResult = self._generate_valid_result()
        validResult['url'] = f"https://twitter.com/{screenName}/status/{tweetId}"

        if status.in_reply_to_user_id_str is not None:
            validResult["code"] = 3
        elif hasattr(status, "retweeted_status"):
            validResult["code"] = 2

        userGroups = self.manager.read_specific_user(screen_name=screenName)
        remainGroupSettings = {}
        for group in userGroups:
            groupSetting = self.manager.read_group_settings(group_id=group)
            if validResult["code"] == 1:
                request = groupSetting['tweet']
            elif validResult["code"] == 2:
                request = groupSetting['retweet']
            else:
                request = groupSetting['comment']
            if request:
                remainGroupSettings[str(group)] = {
                    "translation": groupSetting["translation"],
                    "content": groupSetting["content"],
                    "no-report": groupSetting["no-report"]
                }
        
        if len(remainGroupSettings.keys()) == 0:
            return
        validResult["groups"] = remainGroupSettings
        if hasattr(status, "extended_entities"):
            iterRange = min(4, len(status.extended_entities['media']))
            for i in range(iterRange):
                validResult["mediaUrls"].append(
                    status.extended_entities['media'][i]["media_url_https"])
        
        tweetContent = takeScreenshot(validResult["url"], validResult["code"])
        if tweetContent is None:
            validResult["rawText"] = "服务器错误！"
        elif not tweetContent["status"]:
            validResult["rawText"] = tweetContent["reason"]
        else:
            validResult["screenshotPath"] = tweetContent["screenshotPath"]
            validResult["rawText"] = tweetContent["rawText"]
        with open(f"{TWEET_LOG_PATH}\\{tweetId}.json", "w", encoding="utf-8") as f:
            json.dump(validResult, f, ensure_ascii=False, indent=1)
    
    def on_delete(self, status_id, user_id):
        if str(user_id) not in self.followedUsers:
            return
        if os.path.exists(f"{TWEET_LOG_PATH}\\{status_id}.json"):
            os.remove(f"{TWEET_LOG_PATH}\\{status_id}.json")
            print(f"{user_id}发送的{status_id}被删除！")
        else:
            print(f"{user_id}发送的{status_id}已被删除！")
    
    def on_error(self, status_code):
        self.errList.append(f"服务器错误：{status_code}")

    def on_timeout(self):
        self.errList.append(f"连接超时！")

    def on_disconnect(self, notice):
        self.keep_alive()

    def on_warning(self, notice):
        self.errList.append(f"服务器警告：{notice}")

    def on_exception(self, exception):
        self.errList.append(f"抛出异常：{exception}")
