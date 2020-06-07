import re

from selenium.webdriver import ChromeOptions, Chrome

from .configs import ROOT_PATH

# twemoji emoji转换的中介页面，不需要每次都重启
option = ChromeOptions()
option.headless = True
browser = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
browser.get(f"{ROOT_PATH}server\\bin\\temp.html")


def translate_twemoji_emoji(buf: str) -> str:
    """
    把带有twemoji code的文本内容翻译成带有emoji的文本内容

    :param buf: 带有twemoji code的文本
    :return: twemoji code全部替换为emoji的文本
    """
    # twemoji code被包裹在{}中，使用re找到所有部分
    buffer = re.finditer(r"{\S+?}", buf)
    res = []
    previous_end = 0
    for each in buffer:
        if each.span()[0] != previous_end:
            # 在该twemoji code和上一个twemoji code只间存在文本，将这段文本加入结果
            res.append(buf[previous_end: each.span()[0]])
        # 用temp.html转换twemoji code和emoji
        emoji_code = str(browser.execute_script("return twemoji.convert.fromCodePoint(arguments[0]);",
                                                buf[each.span()[0] + 1: each.span()[1] - 1]))
        # 把emoji加入结果
        res.append(emoji_code)
        # 更改当前结尾位置
        previous_end = each.span()[1]
    if previous_end != len(buf):
        # 加入在最后一个twemoji code之后的文本
        res.append(buf[previous_end:])
    # 拼接结果字符串
    return "".join(res)


def translate_emoji_twemoji(buf: str) -> str:
    """
    把带有emoji的文本内容翻译成带有twemoji code的文本内容

    :param buf: 带有emoji的文本
    :return: 把emoji翻译为twemoji code的文本
    """
    to_change = {}
    for i in range(len(buf)):
        if '\U00010000' < buf[i] < '\U0010ffff':
            # 当前字符为emoji，使用temp.html转换成twemoji code
            twemoji_code = str(browser.execute_script("return twemoji.convert.toCodePoint(arguments[0]);",
                                                      buf[i]))
            to_change[buf[i]] = "{" + twemoji_code + "}"
    for key in to_change.keys():
        buf = buf.replace(key, to_change[key])
    return buf


def process_multiple(block: str) -> dict:
    """
    处理翻译嵌字文本块

    :param block: 翻译文本块
    :return: 每行编号和对应文本，以及最后一个编号
    """
    buffer = re.findall(r"((?P<index>#\d+ )(?P<content>\S+))", block)
    if len(buffer) == 0:
        # 不存在编号命令，错误文本块
        return None
    else:
        res = {}
        for each in buffer:
            res[each[1][1:].strip()] = translate_emoji_twemoji(each[2])
        res['max'] = int(max(res.keys()))
        return res


def process_single(block: str) -> dict:
    """
    处理发推转推嵌字文本块

    :param block: 翻译文本号
    :return: 文本和编号
    """
    return {
        'max': 1,
        '1': translate_emoji_twemoji(block)
    }