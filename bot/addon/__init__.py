from nonebot import on_command, CommandSession, on_request, RequestSession
from nonebot import get_bot, MessageSegment, scheduler
from nonebot.log import logger
from aiocqhttp.exceptions import ActionFailed
from .utils import DatabaseProcessor, add_translation, adjust_group_settings, read_group_settings, ROOT_PATH
from .utils import __A_S__, __A_T__, __c_k__, __c_s__, trans
from .listener import Listener

import json
import os
import tweepy

database_processor = DatabaseProcessor()
bot = get_bot()
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
my_listener = Listener(api=api)
stream_holder = ['author: sudo & sorehait']
stream_holder[0] = tweepy.Stream(api.auth, my_listener)
stream_holder[0].filter(follow=my_listener.followed_users, is_async=True)


@on_request("group")
async def _(session: RequestSession):
    await session.approve()


@on_request("friend")
async def _(session: RequestSession):
    await session.approve()


@on_command("announce", aliases=("a",), only_to_me=False)
async def announce(session: CommandSession):
    groups: list = database_processor.read_all_groups()
    failed = []
    for group in groups:
        try:
            await bot.send_group_msg(group_id=group, message=session.current_arg_text)
        except ActionFailed:
            logger.warning(msg=f"send {group} failed!")
            failed.append(group)
    if len(failed) != 0:
        await session.send(f"发送部分成功！丢失：{failed}")
    else:
        await session.send("发送成功！")


@on_command("style", aliases=("st",), only_to_me=False)
async def adj_style(session: CommandSession):
    buf = session.current_arg_text.strip().split(";")
    if len(buf) != 3:
        session.finish("参数数量错误！请输入三个参数！")
    css_text_template = f"font-family:{buf[0]};font-size:{buf[1]};color:{buf[2]}"
    adjust_group_settings(session.ctx['group_id'], {"css-text": css_text_template})
    await session.send("成功！")


@on_command("help", aliases=("h",), only_to_me=False)
async def get_help(session: CommandSession):
    with open(f"{ROOT_PATH}bin\\help.json", "r", encoding="utf-8") as f:
        res: dict = json.load(f)
    if session.current_arg_text.strip() != "":
        if session.current_arg_text not in res.keys():
            await session.send("未找到该命令！")
        else:
            await session.send(res[session.current_arg_text])
    else:
        await session.send(res["general"])


@on_command("translate", aliases=("tr",), only_to_me=False)
async def get_translation(session: CommandSession):
    if session.is_first_run:
        session.state["index"] = int(session.current_arg_text.strip()) - 1
        session.get("translation", prompt="请输入翻译！")
    else:
        buf = database_processor.read_group_log(session.ctx['group_id'], session.state['index'])
        if buf is None:
            await session.send("index超出范围，请检查！")
        else:
            data = {
                "url": buf[0],
                "tw_type": buf[1],
                "translation": session.state["translation"],
                "group_id": session.ctx['group_id']
            }
            res = add_translation(data)
            if res['status']:
                await session.send(MessageSegment.image(f"file:///{res['filename']}"))
                os.remove(res['filename'])
            else:
                await session.send(res['reason'])


@on_command("add", only_to_me=False)
async def add_new_user(session: CommandSession):
    ops = session.current_arg_text.strip().split(";")
    if len(ops) == 2:
        if not ops[1].isdigit():
            session.finish("错误参数，提示：screen_name在前，id在后！")
        database_processor.add_user(ops[0], ops[1], session.ctx['group_id'])
        stream_holder[0].disconnect()
        my_listener.regenerate_followed_list()
        stream_holder[0] = tweepy.Stream(api.auth, my_listener)
        stream_holder[0].filter(follow=my_listener.followed_users, is_async=True)
        await session.send("成功！")
    else:
        session.finish("参数数量错误！")


@on_command("enable", aliases=("en",), only_to_me=False)
async def enable(session: CommandSession):
    buf = session.current_arg_text.strip().split(";")
    changed = {}
    for each in buf:
        changed[each] = True
    adjust_group_settings(session.ctx['group_id'], changed)
    await session.send("成功！")


@on_command("disable", aliases=("dis",), only_to_me=False)
async def disable(session: CommandSession):
    buf = session.current_arg_text.strip().split(";")
    changed = {}
    for each in buf:
        changed[each] = False
    adjust_group_settings(session.ctx['group_id'], changed)
    await session.send("成功！")


@on_command("no-report", aliases=("no",), only_to_me=False)
async def no_report(session: CommandSession):
    prev: bool = await read_group_settings(session.ctx['group_id'])["no-report"]
    adjust_group_settings(session.ctx['group_id'], {"no-report": not prev})
    await session.send("成功！")


@scheduler.scheduled_job('interval', seconds=60)
async def _():
    cached_files = os.listdir(f"{ROOT_PATH}cache\\")
    limit = 6
    if len(cached_files) < limit:
        limit = len(cached_files)
    if len(my_listener.err_list) > 0:

        stream_holder[0].disconnect()
        my_listener.regenerate_followed_list()
        stream_holder[0] = tweepy.Stream(api.auth, my_listener)
        stream_holder[0].filter(follow=my_listener.followed_users, is_async=True)

        while len(my_listener.err_list) > 0:
            err = my_listener.err_list.pop()
            await bot.send_private_msg(user_id=2267980149, message=f"工口发生！\n{err}")
    for i in range(limit):
        filename = cached_files.pop()
        if not os.path.exists(f"{ROOT_PATH}cache\\{filename}"):
            continue
        with open(f"{ROOT_PATH}cache\\{filename}", "r", encoding="utf-8") as f:
            tweet = json.load(f)

        for group in tweet['groups']:
            index = database_processor.add_group_log(group, tweet['url'], tweet['tw_type'])
            text = f"嵌字编号：{index}"
            current_group_config = tweet['group_configs'][str(group)]
            if not current_group_config['no-report']:
                text = f"原文：{tweet['text']}\n"
                if current_group_config['translation']:
                    text += f"翻译：{trans(tweet['text'])}\n"
                if current_group_config['content']:
                    for each in tweet['content']:
                        text += str(MessageSegment.image(each))
                    text += "\n"
                text += f"嵌字编号：{index}"

            retry_times = 0
            while retry_times < 3:
                try:
                    await bot.send_group_msg(group_id=group, message=MessageSegment.image(f"file:///{tweet['filename']}"))
                    await bot.send_group_msg(group_id=group, message=text)
                    break
                except ActionFailed:
                    retry_times += 1
            if not retry_times < 3:
                logger.warning(f"SEND TO GROUP:{group} FAILED SKIPPED!")

        if os.path.exists(f"{ROOT_PATH}cache\\{filename}"):
            os.remove(f"{ROOT_PATH}cache\\{filename}")
        os.remove(tweet['filename'])
'''
tweet = {
            "url": url,
            "tw_type": tw_type,
            "filename": content['filename'],
            "content": pic_urls,
            "text": content['text'],
            "groups": groups,
            "group_configs": group_configs
        }
'''