import os
import json
import copy
import time

from tweepy import StreamListener

from .db_helper import read_all_user_ids, read_user_groups, read_group_settings
from .server import take_screenshot
from .settings import TWEET_LOG_PATH


class MyStreamListener(StreamListener):

    def reaload_followers(self):
        self.followers = read_all_user_ids()
        print(self.followers)
    
    def __init__(self, api=None):
        super().__init__(api=api)

        self.reaload_followers()
        self.err_list = []
        self.TWEET_TEMPLATE = {
            "url": "",
            "screenshot_path": "",
            "original_text": "",
            "content_urls": [],
            "groups": {}
        }
        self.TWEET_TYPE_SETTING_KEY = ["tweet", "retweet", "comment"]

    def on_status(self, status):
        if status.user.id_str not in self.followers:
            return
        
        screen_name: str = status.user.screen_name
        status_id: str = status.id_str
        twitter_id: str = status.user.id_str
        groups = read_user_groups(twitter_id)

        curr_tweet =copy.deepcopy(self.TWEET_TEMPLATE)
        curr_tweet["url"] = f"https://twitter.com/{screen_name}/status/{status_id}"
        has_content = hasattr(status, "extended_entities")
        content_needed = False
        tweet_listened = False
        tweet_type = 0

        if hasattr(status, "retweeted_status"):
            tweet_type = 1
        elif status.in_reply_to_user_id_str is not None:
            tweet_type = 2
        
        result = take_screenshot(curr_tweet["url"])
        if result["status"]:
            curr_tweet["screenshot_path"] = result["screenshot_path"]
            curr_tweet["original_text"] = result["original_text"]
            for group in groups:
                group_settings = read_group_settings(group)
                group_tweet_listened = self.TWEET_TYPE_SETTING_KEY[tweet_type]
                
                if group_settings[group_tweet_listened]:
                    tweet_listened = True
                    curr_tweet["groups"][group] = {k: v for k, v in group_settings.items() if k not in self.TWEET_TYPE_SETTING_KEY}
                    if has_content and group_settings["content"]:
                        content_needed = True
            if tweet_listened:
                if content_needed:
                    for i in range(min(4, len(status.extended_entities['media']))):
                        curr_tweet["content_urls"].append(status.extended_entities['media'][i]["media_url_https"])
                with open(f"{TWEET_LOG_PATH}\\{screen_name}_{status_id}.json", "w", encoding="utf-8") as f:
                    json.dump(curr_tweet, f, ensure_ascii=False, indent=1)
        else:
            curr_tweet["screenshot_path"] = None
            curr_tweet["original_text"] = result["error"]
            curr_tweet["groups"] = dict().fromkeys(groups, None)
            with open(f"{TWEET_LOG_PATH}\\{screen_name}_{status_id}.json", "w", encoding="utf-8") as f:
                json.dump(curr_tweet, f, ensure_ascii=False, indent=1)
    
    def on_delete(self, status_id, user_id):
        if str(user_id) not in self.followers:
            return
        if os.path.exists(f"{TWEET_LOG_PATH}\\{status_id}.json"):
            with open(f"{TWEET_LOG_PATH}\\{status_id}.json", "r", encoding="utf-8") as f:
                prev = json.load(f)
            os.remove(f"{TWEET_LOG_PATH}\\{status_id}.json")
            if prev["screenshot_path"] is not None and os.path.exists(prev["screenshot_path"]):
                os.remove(prev["screenshot_path"])
            print(f"{user_id}发送的{status_id}被删除！")
        else:
            print(f"{user_id}发送的{status_id}已被删除！")
    
    def on_error(self, status_code):
        self.err_list.append(f"服务器错误：{status_code}")

    def on_timeout(self):
        self.err_list.append(f"连接超时！")

    def on_disconnect(self, notice):
        self.keep_alive()

    def on_warning(self, notice):
        self.err_list.append(f"服务器警告：{notice}")

    def on_exception(self, exception):
        self.err_list.append(f"抛出异常：{exception}")