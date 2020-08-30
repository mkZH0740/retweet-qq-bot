import json
import os

from tweepy import StreamListener

from .settings import SETTING
from .db_holder import databse
from .tweet_holder import Tweet, tweet_queue


class MyListener(StreamListener):
    """
    推文监听流
    """
    followed_users = []
    err_list = []

    def reload_folloed_users(self):
        """
        更新订阅用户列表
        """
        self.followed_users = databse.read_all_user_ids()
        if SETTING.debug:
            print(self.followed_users)

    def get_all_errors(self):
        """
        读取错误列表
        """
        errs = self.err_list.copy()
        self.err_list.clear()
        return errs

    def __init__(self, api=None):
        super().__init__(api=api)

        self.reload_folloed_users()
        self.err_list = []

    def on_status(self, status):
        if status.user.id_str not in self.followed_users:
            # 该流会监听到奇奇怪怪的东西，必须在此过滤掉
            return

        screen_name: str = status.user.screen_name
        status_id: str = status.id_str

        url = f"https://twitter.com/{screen_name}/status/{status_id}"

        user = databse.get_user(screen_name)

        if user is None:
            print(f"WEIRD, {screen_name} is not in database")
            return
        groups = databse.get_user(screen_name).groups

        tweet_type = "tweet"

        if hasattr(status, "retweeted_status"):
            tweet_type = "retweet"
        elif status.in_reply_to_user_id_str is not None:
            tweet_type = "comment"

        contents = []

        if hasattr(status, "extended_entities"):
            # 推文嵌入的图片被保存在extended_entities项目中
            for i in range(min(4, len(status.extended_entities['media']))):
                contents.append(
                    status.extended_entities['media'][i]["media_url_https"])

        tweet_log_path = f"{SETTING.tweet_log_path}\\{status_id}.json"
        # 缓存推文
        with open(tweet_log_path, "w", encoding="utf-8") as f:
            json.dump({"url": url, "tweet_type": tweet_type, "groups": groups,
                       "contents": contents}, f, ensure_ascii=False, indent=4)

        curr_tweet = Tweet(url, tweet_type, groups, contents, tweet_log_path)
        # 通过队列传送给消费者线程
        tweet_queue.put(curr_tweet)

    def on_delete(self, status_id, user_id):
        """
        推文被删除
        """
        screen_name = databse.get_user_id(str(user_id)).screen_name
        if str(user_id) not in self.followed_users:
            return
        log_path = f"{SETTING.tweet_log_path}\\{status_id}.json"
        if os.path.exists(log_path):
            os.remove(log_path)
            print(f"{screen_name}发送的{status_id}被删除！")
        else:
            print(f"{screen_name}发送的{status_id}已被删除！")

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
