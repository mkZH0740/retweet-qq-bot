import os
import tempfile

from PIL import Image
from selenium.webdriver import Chrome
from selenium.common.exceptions import JavascriptException

from .configs import ROOT_PATH


def getPosAndText(driver: Chrome, tw_type: int) -> dict:
    """
    获取目标推特内容的区域左边和内部文本

    :param driver: selenium chrome实例
    :param tw_type: 推特类型代码
    :return: 错误或者推特文本和区域
    """
    with open(f"{ROOT_PATH}server\\bin\\getMainPart.js", "r", encoding="utf-8") as f:
        script = f.read()
    script += "return getMainPart(arguments);"
    try:
        return driver.execute_script(script, tw_type)
    except JavascriptException as e:
        return {'error': e.msg}


def add_translation_js(driver: Chrome, processed_dict: dict, style: str, last_index: int) -> str:
    """
    嵌字脚本

    :param driver: selenium chrome实例
    :param processed_dict: 处理好的文本
    :param style: 样式库
    :param last_index: 最后位置
    :return: 错误文本或无
    """
    with open(f"{ROOT_PATH}server\\bin\\addTranslation.js", "r", encoding="utf-8") as f:
        script = f.read()
    script += "addTranslations(arguments);"
    try:
        driver.execute_script(script, processed_dict, last_index, style)
        return None
    except JavascriptException as e:
        # 脚本运行错误
        return e.msg


def fullscreen(driver: Chrome):
    """
    改变页面大小以显示所有元素，前半部分从splinter库中抄的

    :param driver: selenium chrome实例
    """
    width = driver.execute_script('return Math.max(document.body.scrollWidth, document.body.offsetWidth);')
    height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight);')
    previous_width = driver.get_window_size()['width']
    previous_height = driver.get_window_size()['height']

    width = max(width, previous_width)
    height = max(height, previous_height)

    driver.set_window_size(width, height)
    driver.execute_script('window.scrollTo(document.body.scrollHeight, 0)')


def crop_screenshot(driver: Chrome, bound) -> str:
    """
    截图整个页面，截取目标区域

    :param driver: selenium chrome实例
    :param bound: 区域列表或元组
    :return: 截图文件名
    """

    # 创建临时文件
    (fd, filename) = tempfile.mkstemp(suffix='.png', dir=f'{ROOT_PATH}server\\cache\\')

    os.close(fd)
    driver.save_screenshot(filename)
    img: Image = Image.open(filename)
    img = img.crop(bound)
    img.save(filename)
    return filename