from tweepy.streaming import StreamListener
from .utils import DatabaseProcessor, read_group_settings, get_screenshot, ROOT_PATH

import json
import os


class ErrMsg:
    """
    错误消息类，储存运行时错误
    """
    def __init__(self, message: str, err_type: int):
        self.message = message
        self.err_type = err_type

    def __str__(self):
        if self.err_type == 0:
            return f"流错误：{self.message}"
        else:
            return f"运行时错误：{self.message}"


class Listener(StreamListener):
    """
    tweepy监听流类，监听用户在推特上的行为
    """

    def __init__(self, api=None):
        super().__init__(api)
        # 该类使用的数据处理类
        self.database_processor = DatabaseProcessor()
        # 读取所有需要监听的对象id，必须是str类型
        self.followed_users = [str(user[1]) for user in self.database_processor.read_all_users()]
        # 错误的容器列表
        self.err_list = []
        print(f"INITIALIZATION:{self.followed_users}")
    
    def regenerate_followed_list(self):
        # 重新读取监听对象的id
        self.followed_users = [str(user[1]) for user in self.database_processor.read_all_users()]

    def on_status(self, status):
        if status.user.id_str not in self.followed_users:
            # 其他用户对对象用户的评论也会进入此方法，所以判断一下
            return
        screen_name = status.user.screen_name
        tweet_id = status.id_str
        # 使用mobile网页，因为似乎网页布局更好抓取一点
        url = f'https://mobile.twitter.com/{screen_name}/status/{tweet_id}'
        # 读取该用户所有的监听QQ群号
        groups: list = self.database_processor.read_user(screen_name)
        if groups is None:
            # 该用户被DD们抛弃了，不需要执行接下来的代码
            return
        # dict configs!
        group_configs = {}
        for group in groups:
            # 按群号储存config
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

        if len(groups) < 0:
            # 没有QQ群真正需要当前推文的内容，不需要执行以下代码
            return

        pic_urls = []
        if hasattr(status, 'extended_entities'):
            # 保存推文中所有图片的URL
            for pic in status.extended_entities['media']:
                pic_urls.append(pic['media_url_https'])

        retry_times = 0
        while retry_times < 3:
            # 多试几次，万一通了呢
            content = get_screenshot({"url": url, "tw_type": tw_type})
            if content['status']:
                break
            else:
                print(content['reason'])
                retry_times += 1

        if not retry_times < 3:
            # 出错了，需要发送错误
            content['filename'] = None
            content['text'] = content['reason']

        # 构建tweet数据
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
            # 注意！group_configs中的QQ群号在json文件中从int变为了str
            json.dump(tweet, f, ensure_ascii=False, indent=1)

    def on_exception(self, exception):
        err = ErrMsg(message=f"抛出异常：{exception}", err_type=0)
        self.err_list.append(err)
        return True

    def on_delete(self, status_id, user_id):
        # 用户删除了这条推文，删除还没有被处理的数据文件
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
