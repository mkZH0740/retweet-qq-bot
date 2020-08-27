import json
import threading
import asyncio
import os

from queue import Queue
from typing import List
from nonebot import get_bot, MessageSegment
from aiocqhttp.exceptions import ActionFailed

from .group_settings import group_setting_holder
from .group_log import add_group_log
from .server import baidu_translation, take_screenshot
from .settings import SETTING


bot = get_bot()
tweet_queue = Queue()


class Tweet:
    url: str
    tweet_type: str
    tweet_log_path: str
    contents: List[str] = []
    groups: List[str] = []

    def __init__(self, url: str, tweet_type: str, groups: List[str], contents: List[str], tweet_log_path: str):
        self.url = url
        self.tweet_type = tweet_type
        self.groups = groups
        self.contents = contents
        self.tweet_log_path = tweet_log_path


async def send_with_retry(msg: str, group_id: int, time: int = 0):
    if time > 2:
        return
    if SETTING.debug and time == 0:
        print("============== sending ===============")
    try:
        await bot.send_group_msg(group_id=group_id, message=msg)
    except ActionFailed as e:
        if e.retcode == -11:
            print("send failed -11, retrying")
            await send_with_retry(msg, group_id, time + 1)
        else:
            print(f"send failed, retcode={e.retcode} @ {group_id}")
            return


async def send_msg(success_result: dict, tweet: Tweet):
    screenshot_path = success_result["msg"]
    original_text = success_result["content"]
    translated_text = await baidu_translation(original_text)

    screenshot_msg = str(MessageSegment.image(f"file:///{screenshot_path}"))
    content_msg = [str(MessageSegment.image(content_url))
                   for content_url in tweet.contents]

    for group in tweet.groups:
        group_setting = group_setting_holder.get(group)
        if not group_setting.get(tweet.tweet_type, False):
            continue
        current_msg = ""
        if group_setting["original_text"]:
            current_msg += f"原文：{original_text}\n"
        if group_setting["translate"]:
            current_msg += f"翻译：{translated_text}\n"
        if group_setting["content"]:
            current_msg += f"附件：" + "".join(content_msg)
        group_log_index = add_group_log(group, tweet.url)
        current_msg += f"\n嵌字编号：{group_log_index}"

        current_msg = current_msg.encode("utf-16", "surrogatepass").decode("utf-16")

        await send_with_retry(screenshot_msg, int(group))
        await send_with_retry(current_msg, int(group))

    print(f"SEND {tweet.url} finished!")
    if os.path.exists(tweet.tweet_log_path):
        os.remove(tweet.tweet_log_path)


async def send_fail_msg(failed_result: dict, tweet: Tweet):
    failed_msg = failed_result.get(
        "msg", f"unknown error occured on server @ {tweet.url}")
    for group in tweet.groups:
        await send_with_retry(failed_msg, group_id=group)


async def send_tweet(tweet: Tweet):
    screenshot_result: dict = await take_screenshot(tweet.url)
    if screenshot_result.get("status", False):
        # succeed
        await send_msg(screenshot_result, tweet)
    else:
        # failed
        await send_fail_msg(screenshot_result, tweet)


async def tweet_consumer():
    while True:
        print("asking for tweet")
        curr_tweet: Tweet = tweet_queue.get()
        await send_tweet(curr_tweet)


class Wrapper(threading.Thread):

    def load(self):
        cached_tweet_filenames = os.listdir(SETTING.tweet_log_path)
        for tweet_filename in cached_tweet_filenames:
            with open(f"{SETTING.tweet_log_path}\\{tweet_filename}", "r", encoding="utf-8") as f:
                curr_tweet_raw = json.load(f)
            curr_tweet = Tweet(curr_tweet_raw["url"], curr_tweet_raw["tweet_type"], curr_tweet_raw["groups"], curr_tweet_raw["contents"], f"{SETTING.log_path}\\{tweet_filename}")
            tweet_queue.put(curr_tweet)
            if SETTING.debug:
                print(f"CACHED TWEET {tweet_filename} LOADED!")


    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        consumer = asyncio.ensure_future(tweet_consumer())
        loop.run_until_complete(consumer)
        loop.close()

