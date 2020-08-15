import os
import json
import requests

from tweepy import OAuthHandler, API, Stream
from aiocqhttp.exceptions import ActionFailed
from nonebot import get_bot, CommandSession, on_command, MessageSegment, scheduler

from .db_helper import read_group_settings, read_all_groups, add_user, add_group_log
from .settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, SUCCEED_MSG, EXCEPTION_MSG, TWEET_LOG_PATH
from .listener import MyStreamListener
from .server import baidu_translation


bot = get_bot()
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = API(auth)
listener = MyStreamListener(api)
stream_holder = [""]
stream_holder[0] = Stream(auth=api.auth, listener=listener)
stream_holder[0].filter(follow=listener.followers, is_async=True)


def get_twitter_id(screen_name: str) -> str:
    res = requests.post(url="https://tweeterid.com/ajax.php", data=f"input={screen_name.lower()}", headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}).content.decode("utf-8")
    return res


async def send_group_msgs(groups: list, msg: str):
    """
    包装发送群消息的函数
    """
    try:
        # 循环发送消息
        while len(groups) > 0:
            current_group = groups.pop()
            await bot.send_group_msg(group_id=int(current_group), message=msg)
    except ActionFailed as e:
        # 打印捕捉到的异常，跳过当前群继续执行
        print(f"{e.retcode} @ {current_group}")
        await send_group_msgs(groups, msg)

def refresh_stream():
    """
    刷新当前的tweepy流
    """
    stream_holder[0].disconnect()
    # 重取监听对象的twitter id
    listener.reaload_followers()
    stream_holder[0] = Stream(api.auth, listener)
    stream_holder[0].filter(follow=listener.followers, is_async=True)


@on_command("announce", aliases='a', only_to_me=False)
async def announce_command(session: CommandSession):
    """
    向所有存在监听对象的群发送消息
    """
    groups = read_all_groups()
    await send_group_msgs(groups, session.current_arg_text.strip())


@on_command("add", only_to_me=False)
async def add_command(session: CommandSession):
    screen_name = session.current_arg_text.strip()
    twitter_id = get_twitter_id(screen_name)
    if not twitter_id.isdigit():
        session.finish("请输入正确的screen name")
    if add_user(screen_name, twitter_id, str(session.event.group_id)):
        refresh_stream()
        session.finish(SUCCEED_MSG)
    else:
        session.finish(EXCEPTION_MSG)


@scheduler.scheduled_job('interval', seconds=60)
async def _schedule():
    cached_logs = os.listdir(f"{TWEET_LOG_PATH}\\")
    if len(listener.err_list) > 0:
        current_err_list = listener.err_list.copy()
        listener.err_list.clear()
        refresh_stream()
        await bot.send_private_msg(user_id=2267980149, message=f"出现错误 => {current_err_list}")
    for _ in range(min(5, len(cached_logs))):
        log_filename = cached_logs.pop()
        log_path = f"{TWEET_LOG_PATH}\\{log_filename}"
        if not os.path.exists(log_path):
            continue
        with open(log_path, "r", encoding="utf-8") as f:
            tweet_content = json.load(f)
        os.remove(log_path)

        original_text = tweet_content["original_text"]
        screenshot_path = tweet_content["screenshot_path"]
        groups = list(tweet_content["groups"].keys())
        if screenshot_path is None:
            await send_group_msgs(groups, original_text)
        else:
            screenshot_msg = str(MessageSegment.image(f"file:///{screenshot_path}"))
            content_msg = "".join([str(MessageSegment.image(url)) for url in tweet_content['content_urls']])
            for group, group_settings in tweet_content["groups"].items():
                current_msg = screenshot_msg + "\n"
                if group_settings["original_text"]:
                    current_msg += f"原文: {original_text}\n"
                if group_settings["translate"]:
                    current_msg += f"翻译: {await baidu_translation(original_text)}\n"
                if group_settings["content"] and current_msg!= "":
                    current_msg += f"附件: {content_msg}\n"
                index = add_group_log(group, tweet_content["url"])
                current_msg += f"嵌字编号: {index}"
                current_msg = str(current_msg).encode("utf-16", "surrogatepass").decode("utf-16")
                try:
                    await bot.send_group_msg(group_id=int(group), message=current_msg)
                except ActionFailed as e:
                    print(f"sending to @ {group} failed, retcode {e.retcode}")
            os.remove(screenshot_path)
