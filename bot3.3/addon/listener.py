'''
@author: sudo

'''
from tweepy import StreamListener
from .utils import generate_local_tweet_log ,read_all_users, read_groups_of_user, get_group_config
import json


class MyStreamListener(StreamListener):
    def build_up(self):
        self.err_list = list()
        self.followed_users = read_all_users()
        print(self.followed_users)
    
    def on_status(self, status):
        if status.user.id_str in self.followed_users:
            screen_name = status.user.screen_name
            tweet_id = status.id_str
            url = f'https://mobile.twitter.com/{screen_name}/status/{tweet_id}'
            groups = read_groups_of_user(screen_name)

            if hasattr(status, 'retweeted_status'):
                for group in groups:
                    config = get_group_config(group)['retweet']
                    if not config:
                        groups.remove(group)
                tw_type = 2
            elif status.in_reply_to_status_id is not None:
                for group in groups:
                    config = get_group_config(group)['comment']
                    if not config:
                        groups.remove(group)
                tw_type = 3
            else:
                for group in groups:
                    config = get_group_config(group)['tweet']
                    if not config:
                        groups.remove(group)
                tw_type = 1

            if len(groups) > 0:
                pic_urls = []
                if hasattr(status, 'extended_entities'):
                    for pic in status.extended_entities['media']:
                        pic_urls.append(pic['media_url_https'])
                tweet = {
                    'url': url,
                    'tw_type': tw_type,
                    'groups': groups,
                    'pic_urls': pic_urls
                }
                print(tweet)
                generate_local_tweet_log(tweet,tweet_id)

    def on_exception(self, exception):
        msg = "致命异常" + str(exception)
        self.err_list.append(msg)
        return True

    def on_disconnect(self, notice):
        msg = "丢失链接:" + str(notice)
        self.err_list.append(msg)
        return True

    def on_error(self, status_code):
        msg = "工口发生:" + str(status_code)
        self.err_list.append(msg)
        return True

    def on_warning(self, notice):
        msg = "服务器警告：" + str(notice)
        self.err_list.append(msg)
        return True

    def on_timeout(self):
        msg = "超时"
        self.err_list.append(msg)
        return True
