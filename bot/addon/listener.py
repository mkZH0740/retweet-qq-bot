from tweepy.streaming import StreamListener
from .utils import DatabaseProcessor, read_group_settings, get_screenshot, ROOT_PATH

import json
import os


class ErrMsg:
    def __init__(self, message: str, err_type: int):
        self.message = message
        self.err_type = err_type

    def __str__(self):
        if self.err_type == 0:
            return f"流错误：{self.message}"
        else:
            return f"运行时错误：{self.message}"


class Listener(StreamListener):

    def __init__(self, api=None):
        super().__init__(api)
        self.database_processor = DatabaseProcessor()
        self.followed_users = [str(user[1]) for user in self.database_processor.read_all_users()]
        self.err_list = []
        print(f"INITIALIZATION:{self.followed_users}")

    def regenerate_followed_list(self):
        self.followed_users = [str(user[1]) for user in self.database_processor.read_all_users()]

    def on_status(self, status):
        if status.user.id_str not in self.followed_users:
            return
        screen_name = status.user.screen_name
        tweet_id = status.id_str
        url = f'https://mobile.twitter.com/{screen_name}/status/{tweet_id}'
        groups: list = self.database_processor.read_user(screen_name)
        if groups is None:
            return
        # dict configs!
        group_configs = {}
        for group in groups:
            group_configs[group] = read_group_settings(group)
        if hasattr(status, "retweeted_status"):
            # retweet
            for group in groups:
                if not group_configs[group]['retweet']:
                    groups.remove(group)
                    group_configs.pop(group)
            tw_type = 2
        elif status.in_reply_to_status_id is not None:
            # comment
            for group in groups:
                if not group_configs[group]['comment']:
                    groups.remove(group)
                    group_configs.pop(group)
            tw_type = 3
        else:
            # normal tweet
            for group in groups:
                if not group_configs[group]['tweet']:
                    groups.remove(group)
                    group_configs.pop(group)
            tw_type = 1

        pic_urls = []
        if hasattr(status, 'extended_entities'):
            for pic in status.extended_entities['media']:
                pic_urls.append(pic['media_url_https'])

        retry_times = 0
        while retry_times < 3:
            content = get_screenshot({"url": url, "tw_type": tw_type})
            if content['status']:
                break
            else:
                print(content['reason'])
                retry_times += 1
        if not retry_times < 3:
            return

        tweet = {
            "url": url,
            "tw_type": tw_type,
            "filename": content['filename'],
            "content": pic_urls,
            "text": content['text'],
            "groups": groups,
            "group_configs": group_configs
        }

        with open(f"{ROOT_PATH}cache//{tweet_id}.json", "w", encoding="utf-8") as f:
            json.dump(tweet, f, ensure_ascii=False, indent=1)

    def on_exception(self, exception):
        err = ErrMsg(message=f"抛出异常：{exception}", err_type=0)
        self.err_list.append(err)
        return True

    def on_delete(self, status_id, user_id):
        if os.path.exists(f"{ROOT_PATH}cache//{status_id}.json"):
            os.remove(f"{ROOT_PATH}cache//{status_id}.json")
        else:
            print(f"{status_id} already gone!")
        return True

    def on_error(self, status_code):
        err = ErrMsg(message=f"服务器错误：{status_code}", err_type=0)
        self.err_list.append(err)
        return True

    def on_timeout(self):
        err = ErrMsg(message=f"连接超时!", err_type=0)
        self.err_list.append(err)
        return True

    def on_disconnect(self, notice):
        self.keep_alive()
        return True

    def on_warning(self, notice):
        err = ErrMsg(message=f"服务器警告：{notice}", err_type=0)
        self.err_list.append(err)
        return True
