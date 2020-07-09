from nonebot import scheduler, on_command, CommandSession, get_bot, MessageSegment
from aiocqhttp import ActionFailed
from tweepy import API, OAuthHandler, Stream

from .listenerHelper import MyListener
from .serverHelper import addTranslation, baiduTranslation
from .settingHelper import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET, PROJECT_PATH, GROUP_SETTING_PATH, TWEET_LOG_PATH
from .databaseHelper import DBManager

import json
import os
import requests

bot = get_bot()
manager = DBManager()
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = API(auth)
currListener = MyListener(api=api)
stream_holder = ['author: sudo & SoreHait']
stream_holder[0] = Stream(api.auth, currListener)
stream_holder[0].filter(follow=currListener.followedUsers, is_async=True)


async def my_send_group_msg(group_id: int, message: str):
    try:
        await bot.send_group_msg(group_id=group_id, message=message)
    except ActionFailed as e:
        if e.retcode != -34:
            await bot.send_group_msg(group_id=group_id, message="发送失败")
        else:
            print(f"在{group_id}被禁言！")


@on_command("help", only_to_me=False)
async def commandHelp(session: CommandSession):
    with open(f"{PROJECT_PATH}\\help.json", "r", encoding="utf-8") as f:
        helpContent = json.load(f)
    targetCommand = session.current_arg_text.strip()
    if len(targetCommand) == 0:
        await session.send(message=helpContent['default'])
    elif targetCommand in helpContent:
        await session.send(message=helpContent[targetCommand])
    else:
        await session.send("该命令不存在！")


@on_command("translation", aliases='tr', only_to_me=False)
async def commandTranslate(session: CommandSession):
    if session.is_first_run:
        index = session.current_arg_text
        if index.isdigit():
            session.state["index"] = int(index)
            session.get("translation", prompt="请输入翻译：")
        else:
            session.finish("嵌字编号必须是数字！")
    else:
        groupLog = manager.read_group_log(group_id=session.event.group_id, index=session.state["index"])
        if groupLog is None:
            session.finish(message="非法编号")
        groupSetting = manager.read_group_settings(group_id=session.event.group_id)
        result = addTranslation(groupLog["url"], groupLog["code"], session.state["translation"], 
            groupSetting["tag"], groupSetting["css-text"])
        print(result)
        if result is None:
            await session.send("服务器内部错误")
        elif not result["status"]:
            await session.send(result["reason"])
        else:
            try:
                await session.send(MessageSegment.image(f"file:///{result['screenshotPath']}"))
                os.remove(result['screenshotPath'])
            except ActionFailed as e:
                print(f"#tr 发生错误 => {e.retcode}")
                await session.send("发送消息失败")


@on_command("announce", only_to_me=False)
async def commandAnnounce(session: CommandSession):
    groups = manager.read_all_groups()
    for group in groups:
        try:
            await bot.send_group_msg(group_id=group, message=session.current_arg_text)
        except ActionFailed as e:
            await session.send(message=f"发送{group}错误，代码{e.retcode}")


@on_command("tag", only_to_me=False)
async def commandChangeTag(session: CommandSession):
    imgTag = session.current_arg_images
    if len(imgTag) != 1:
        session.finish(message="请输入一个tag图片！")
    else:
        img = requests.get(imgTag[0])
        with open(f"{GROUP_SETTING_PATH}\\{session.event.group_id}_tag.png", "wb") as f:
            f.write(img.content)
        manager.adjust_group_settings(group_id=session.event.group_id, 
            adjusted_value={"tag": f"{GROUP_SETTING_PATH}\\{session.event.group_id}_tag.png"})
        await session.send("成功！")


@scheduler.scheduled_job('interval', seconds=60)
async def _():
    cachedLogs = os.listdir(f"{TWEET_LOG_PATH}\\")
    limit = min(5, len(cachedLogs))
    if len(currListener.errList) > 0:
        bufferedErrlist = []
        while len(currListener.errList) > 0:
            bufferedErrlist.append(currListener.errList.pop())
        stream_holder[0].disconnect()
        currListener.regenerate_followed_users()
        stream_holder[0] = Stream(api.auth, currListener)
        stream_holder[0].filter(follow=currListener.followedUsers, is_async=True)
        await bot.send_private_msg(user_id=2267980149, message=f"出现错误 => {bufferedErrlist}")
    
    for i in range(limit):
        tweetLogFile = cachedLogs.pop()
        tweetLogPath = f"{TWEET_LOG_PATH}\\{tweetLogFile}"
        if not os.path.exists(tweetLogPath):
            continue

        with open(tweetLogPath, "r", encoding="utf-8") as f:
            tweetContent = json.load(f)
        os.remove(tweetLogPath)

        groups = [int(group) for group in tweetContent["groups"]]

        if tweetContent["screenshotPath"] is None:
            errMessage = f"遇到错误 => {tweetContent['url']}处发生了{tweetContent['rawText']}"
            for group in groups:
                await my_send_group_msg(group_id=group, message=errMessage)
        else:
            screenshotMsg = str(MessageSegment.image(f"file:///{tweetContent['screenshotPath']}"))
            mediaContentMsg = "".join([str(MessageSegment.image(url)) for url in tweetContent['mediaUrls']])
            for group in groups:
                currMsg = screenshotMsg + "\n"
                currGroupConfig = tweetContent["groups"][str(group)]
                if not currGroupConfig["no-report"]:
                    currMsg += f"原文：{tweetContent['rawText']}\n"
                    if currGroupConfig["translation"]:
                        currMsg += f"翻译：{baiduTranslation(tweetContent['rawText'])}\n"
                    if currGroupConfig["content"]:
                        currMsg += mediaContentMsg
                
                index = manager.add_group_log(group_id=group, url=tweetContent["url"], code=tweetContent["code"])
                currMsg += f"嵌字编号：{index}"
                currMsg = currMsg.encode("utf-16", "surrogatepass").decode("utf-16")

                await my_send_group_msg(group_id=group, message=currMsg)

        if tweetContent["screenshotPath"] is not None:
            os.remove(tweetContent["screenshotPath"])
