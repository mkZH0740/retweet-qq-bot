import re

from selenium.webdriver import ChromeOptions, Chrome

from .configs import ROOT_PATH

option = ChromeOptions()
option.headless = True
browser = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
browser.get(f"{ROOT_PATH}server\\bin\\temp.html")


def _get_twemoji_id(buf: str) -> list:
    args = []
    curr = ""
    for i in range(len(buf)):
        if '\U00010000' < buf[i] < '\U0010ffff':
            if len(curr) > 0:
                args.append(curr)
                args.append(buf[i])
                curr = ""
            else:
                args.append(buf[i])
        else:
            curr += buf[i]
            if i == len(buf) - 1:
                args.append(curr)

    for i in range(len(args)):
        if '\U00010000' < args[i] < '\U0010ffff':
            args[i] = "{emj}" + browser.execute_script("return grabTheRightIcon(arguments[0])", args[i])
    return args
    

def process_multiple(block: str) -> list:
    buffer = re.findall(r"((?P<index>#\d+ )(?P<content>\S+))", block)
    if len(buffer) == 0:
        return None
    else:
        # [('#1 测试2#234', '#1 ', '测试2#234'), ('#3 测试3', '#3 ', '测试3')]
        # process emjs
        res = []
        for each in buffer:
            current_line = [each[1], _get_twemoji_id(each[2])]
            res.append(current_line)
        return res


def process_single(block: str) -> list:
    return _get_twemoji_id(block)