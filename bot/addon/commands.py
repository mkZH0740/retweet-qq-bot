import os
import json
import requests

from aiocqhttp import ActionFailed
from nonebot import on_command, CommandSession, on_request, RequestSession, get_bot, MessageSegment

from .group_settings import group_setting_holder
from .group_log import read_group_log
from .settings import SETTING
from .db_holder import databse
from .server import add_translation, take_screenshot

bot = get_bot()

unknown_error = "unknown error on server, nothing is returned"


@on_request('group')
async def answer_req_group(session: RequestSession):
    await session.approve()
    group_setting_holder.get(str(session.event.group_id))


@on_request('friend')
async def answer_req_friend(session: RequestSession):
    await session.approve()


def check_is_url(content: str):
    return (content.startswith("https://twitter.com") or content.startswith("https://mobile.twitter.com"))


@on_command("announce", only_to_me=False)
async def announce_command(session: CommandSession):
    all_groups = databse.read_all_groups()
    for group in all_groups:
        try:
            await bot.send_group_msg(group_id=int(group), message=session.current_arg_text.strip())
        except ActionFailed as e:
            print(f"{e.retcode} @ {group}")


@on_command("help", only_to_me=False)
async def help_command(session: CommandSession):
    with open("help.json", "r", encoding="utf-8") as f:
        help_contents: dict = json.load(f)
    args = session.current_arg_text.strip()
    # 按照args寻找对应帮助条目，不存在则返回默认条目
    content = help_contents.get(args, help_contents["default"])
    session.finish(content)


@on_command("enable", only_to_me=False)
async def enable_command(session: CommandSession):
    keys = session.current_arg_text.split(";")
    # 为每个args初始化值为True
    change = dict.fromkeys(keys, True)
    try:
        group_setting_holder.update(str(session.event.group_id), change)
        session.finish("成功")
    except Exception as e:
        await bot.send_private_msg(user_id=2267980149, message=f"@ {session.event.group_id} => {e}")
        session.finish("未知错误，失败")


@on_command("disable", only_to_me=False)
async def enable_command(session: CommandSession):
    keys = session.current_arg_text.split(";")
    # 为每个args初始化值为False
    change = dict.fromkeys(keys, False)
    try:
        group_setting_holder.update(str(session.event.group_id), change)
        session.finish("成功")
    except Exception as e:
        await bot.send_private_msg(user_id=2267980149, message=f"@ {session.event.group_id} => {e}")
        session.finish("未知错误，失败")


@on_command("tag", only_to_me=False)
async def tag_command(session: CommandSession):
    tag_img = session.current_arg_images
    if len(tag_img) != 1:
        session.finish("请输入一个tag图片！")
    buf = requests.get(tag_img[0])
    tag_path = f"{SETTING.group_tag_path}\\{session.event.group_id}_tag.png"
    with open(tag_path, "wb") as f:
        f.write(buf.content)
    group_setting_holder.update(
        str(session.event.group_id), {"tag_path": tag_path})
    session.finish("成功")


@on_command("css", only_to_me=False)
async def css_command(session: CommandSession):
    """
    设置嵌字时文字span的css样式
    """
    css_text = session.current_arg_text.strip()
    if not css_text.startswith(".text"):
        session.finish("格式错误，请按照css格式定义.text{}！")
    css_path = f"{SETTING.group_css_path}\\{session.event.group_id}_text.css"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_text)
    group_setting_holder.update(
        str(session.event.group_id), {"css_path": css_path})
    session.finish("成功")


@on_command("checkcss", only_to_me=False)
async def check_css_command(session: CommandSession):
    """
    获取当前使用的css样式
    """
    css_path = group_setting_holder.get(
        str(session.event.group_id))["css_path"]
    with open(css_path, "r", encoding="utf-8") as f:
        res = f.read()
    session.finish(res)


@on_command("translate", aliases='tr', only_to_me=False)
async def translate_command(session: CommandSession):
    if session.is_first_run:
        index = session.current_arg_text.strip()
        if not index.isdigit():
            session.finish("请输入嵌字编号！")
        session.state["index"] = int(index) - 1
        session.get("translation", prompt="请输入翻译")
    try:
        url = read_group_log(str(session.event.group_id),
                             session.state["index"])
        group_settings = group_setting_holder.get(str(session.event.group_id))
        result = await add_translation(
            url, session.state["translation"], group_settings)
        if result.get("status", False):
            await session.send(str(MessageSegment.image(f"file:///{result['msg']}")))
            os.remove(result["msg"])
        else:
            await session.send(result.get("msg", unknown_error))
    except RuntimeError as e:
        session.finish(str(e))


@on_command("screenshot", only_to_me=False)
async def screenshot_command(session: CommandSession):
    url = session.current_arg_text.strip()
    if check_is_url(url):
        session.finish("请输入正确的url")
    result = await take_screenshot(url)
    if result.get("status", False):
        # 文字中的emoji不能直接发送，必须进行转码
        text = result['content'].encode(
            "utf-16", "surrogatepass").decode("utf-16")
        await session.send(str(MessageSegment.image(f"file:///{result['msg']}")) + f"\n原文：{text}")
        os.remove(result["msg"])
    else:
        await session.send(result.get("msg", unknown_error))


@on_command("freetranslate", aliases='ftr', only_to_me=False)
async def free_translate_command(session: CommandSession):
    if session.is_first_run:
        url = session.current_arg_text.strip()
        if check_is_url(url):
            session.finish("请输入正确的url")
        session.state["url"] = url
        session.get("translation", prompt="请输入翻译")
    try:
        group_settings = group_setting_holder.get(str(session.event.group_id))
        result = await add_translation(
            session.state["url"], session.state["translation"], group_settings)
        if result.get("status", False):
            await session.send(str(MessageSegment.image(f"file:///{result['msg']}")))
            os.remove(result["msg"])
        else:
            await session.send(result.get("msg", unknown_error))
    except RuntimeError as e:
        session.finish(str(e))
