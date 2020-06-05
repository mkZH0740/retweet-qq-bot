import re

from selenium.webdriver import ChromeOptions, Chrome

from .configs import ROOT_PATH

option = ChromeOptions()
option.headless = True
browser = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
browser.get(f"{ROOT_PATH}server\\bin\\temp.html")


def translate_twemoji_emoji(buf: str) -> str:
    buffer = re.finditer(r"{\S+?}", buf)
    res = []
    previous_end = 0
    for each in buffer:
        if each.span()[0] != previous_end:
            res.append(buf[previous_end: each.span()[0]])
        emoji_code = str(browser.execute_script("return twemoji.convert.fromCodePoint(arguments[0]);",
                                                buf[each.span()[0] + 1: each.span()[1] - 1]))
        res.append(emoji_code)
        previous_end = each.span()[1]
    if previous_end != len(buf):
        res.append(buf[previous_end:])
    return "".join(res)


def translate_emoji_twemoji(buf: str) -> str:
    to_change = {}
    for i in range(len(buf)):
        if '\U00010000' < buf[i] < '\U0010ffff':
            twemoji_code = str(browser.execute_script("return twemoji.convert.toCodePoint(arguments[0]);",
                                                      buf[i]))
            to_change[buf[i]] = "{" + twemoji_code + "}"
    for key in to_change.keys():
        buf = buf.replace(key, to_change[key])
    return buf


def process_multiple(block: str) -> dict:
    buffer = re.findall(r"((?P<index>#\d+ )(?P<content>\S+))", block)
    if len(buffer) == 0:
        return None
    else:
        res = {}
        for each in buffer:
            res[each[1][1:].strip()] = translate_emoji_twemoji(each[2])
        res['max'] = int(max(res.keys()))
        return res


def process_single(block: str) -> dict:
    return {
        'max': 1,
        '1': translate_emoji_twemoji(block)
    }