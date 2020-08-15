import requests
import json

from nonebot import CommandSession, on_command, RequestSession, on_request, MessageSegment
from typing import List

from .db_helper import add_user, add_group_settings, read_group_settings, read_group_log, DEFAULT_GROUP_SETTINGS
from .settings import TAG_PATH, CSS_PATH, SUCCEED_MSG, EXCEPTION_MSG
from .server import add_translation, take_screenshot


# 处理加好友加群请求
@on_request('group')
async def answer_req_group(session: RequestSession):
    await session.approve()
    
@on_request('friend')
async def answer_req_friend(session: RequestSession):
    await session.approve()


def generate_simple_set(value: bool, keys: List[str]):
    result = {}
    for key in keys:
        previous_value = DEFAULT_GROUP_SETTINGS.get(key)
        if type(previous_value) == bool:
            result[key] = value
    return result


def check_is_url(content: str):
    return (content.startswith("https://twitter.com") or content.startswith("https://mobile.twitter.com"))


@on_command("help", only_to_me=False)
async def help_command(session: CommandSession):
    with open("help.json", "r", encoding="utf-8") as f:
        help_contents: dict = json.load(f)
    args = session.current_arg_text.strip()
    content = help_contents.get(args, help_contents["default"])
    session.finish(content)


@on_command("enable", only_to_me=False)
async def enable_command(session: CommandSession):
    result = generate_simple_set(True, session.current_arg_text.strip().split(";"))
    try:
        add_group_settings(str(session.event.group_id), result)
        session.finish(SUCCEED_MSG)
    except Exception as e:
        print(e)
        session.finish(EXCEPTION_MSG)


@on_command("disable", only_to_me=False)
async def disable_command(session: CommandSession):
    result = generate_simple_set(False, session.current_arg_text.strip().split(";"))
    try:
        add_group_settings(str(session.event.group_id), result)
        session.finish(SUCCEED_MSG)
    except Exception as e:
        print(e)
        session.finish(EXCEPTION_MSG)


@on_command("tag", only_to_me=False)
async def tag_command(session: CommandSession):
    tag_img = session.current_arg_images
    if len(tag_img) != 1:
        session.finish("请输入一个tag图片！")
    buf = requests.get(tag_img[0])
    tag_path = f"{TAG_PATH}\\{session.event.group_id}_tag.png"
    with open(tag_path, "wb") as f:
        f.write(buf.content)
    add_group_settings(str(session.event.group_id), {"tag_path": tag_path})
    session.finish(SUCCEED_MSG)


@on_command("css", only_to_me=False)
async def css_command(session: CommandSession):
    """
    设置嵌字时文字span的css样式
    """
    css_text = session.current_arg_text.strip()
    if not css_text.startswith(".text"):
        session.finish("格式错误，请按照css格式定义.text{}！")
    css_path = f"{CSS_PATH}\\{session.event.group_id}_text.css"
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_text)
    add_group_settings(str(session.event.group_id), {"css_path": css_path})
    session.finish("成功")


@on_command("checkcss", only_to_me=False)
async def check_css_command(session: CommandSession):
    """
    获取当前使用的css样式
    """
    css_path = read_group_settings(str(session.event.group_id))["css_path"]
    with open(css_path, "r", encoding="utf-8") as f:
        res = f.read()
    await session.send(res)


@on_command("translate", aliases='tr', only_to_me=False)
async def translate_command(session: CommandSession):
    if session.is_first_run:
        index = session.current_arg_text.strip()
        if not index.isdigit():
            session.finish("请输入嵌字编号！")
        session.state["index"] = int(index) - 1
        session.get("translation", prompt="请输入翻译")
    try:
        url = read_group_log(str(session.event.group_id), session.state["index"])
        group_settings = read_group_settings(str(session.event.group_id))
        result = add_translation(url, session.state["translation"], group_settings)
        if result["status"]:
            await session.send(str(MessageSegment.image(f"file:///{result['screenshot_path']}")))
        else:
            await session.send(result["error"])
    except RuntimeError as e:
        session.finish(str(e))


@on_command("screenshot", only_to_me=False)
async def screenshot_command(session: CommandSession):
    url = session.current_arg_text.strip()
    if check_is_url(url):
        session.finish("请输入正确的url")
    result = take_screenshot(url)
    if result["status"]:
        await session.send(str(MessageSegment.image(f"file:///{result['screenshot_path']}")) + f"\n原文：{result['original_text']}")
    else:
        await session.send(result["error"])


@on_command("freetranslate", aliases='ftr', only_to_me=False)
async def free_translate_command(session: CommandSession):
    if session.is_first_run:
        url = session.current_arg_text.strip()
        if check_is_url(url):
            session.finish("请输入正确的url")
        session.state["url"] = url
        session.get("translation", prompt="请输入翻译")
    try:
        group_settings = read_group_settings(str(session.event.group_id))
        result = add_translation(session.state["url"], session.state["translation"], group_settings)
        if result["status"]:
            await session.send(str(MessageSegment.image(f"file:///{result['screenshot_path']}")))
        else:
            await session.send(result["error"])
    except RuntimeError as e:
        session.finish(str(e))
        