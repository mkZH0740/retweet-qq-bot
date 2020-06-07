import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait

from .configs import ROOT_PATH
from .text_processor import process_multiple, process_single
from .utils import getPosAndText, fullscreen, crop_screenshot, add_translation_js


def logging(translation: str, processed_translation: list, style: str, url: str, tw_type: int, error: str):
    """
    简单的log函数

    :param translation: 翻译文本
    :param processed_translation: 处理后的翻译文本
    :param style: 样式
    :param url: 推特URL
    :param tw_type: 推特类型代码
    :param error: 错误原因
    """
    with open("err_log.txt", "a+", encoding="utf-8") as f:
        log = "\n\n"
        log += f"url: {url}; tw_type: {tw_type}\n"
        log += f"translation: {translation}\n"
        log += f"processed: {processed_translation}\n"
        log += f"style: {style}\n"
        log += f"error: {error}"
        f.write(log)


async def add_translation(translation: str, style: str, url: str, tw_type: int) -> dict:
    # 为每个任务新建无头chrome
    option = ChromeOptions()
    option.headless = True
    driver = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
    driver.get(url)
    driver.set_window_size(1920, 1080)
    try:
        # 等待8秒定位页面中的元素，定位不到则很有可能推特已被删除，返回运行不成功的status
        WebDriverWait(driver, 8).until(lambda x: x.find_element_by_css_selector('article>div'))
    except TimeoutException:
        driver.quit()
        return {"status": False, "reason": "tweet may be deleted!"}
    # 额外等待一小会儿，让图片加载
    time.sleep(0.5)

    # 修改无头chrome的页面大小以容纳推文全部内容
    fullscreen(driver)

    if tw_type == 3:
        # 评论嵌字，需要处理多行
        processed = process_multiple(translation)
    else:
        # 单行嵌字
        processed = process_single(translation)

    # 最大序号
    last_index = processed.pop('max')
    # 加入翻译文本
    res = add_translation_js(driver, processed, style, last_index)

    if res is None:
        # 尝试获取推文内容在页面上的位置和内部的文本
        result = getPosAndText(driver, tw_type)
        if 'error' in result:
            driver.quit()
            return {"status": False, "reason": result['error']}
        buf = result['position']
        bound = (buf['left'], buf['top'], buf['right'], buf['bottom'])
        filename = crop_screenshot(driver, bound)
        driver.quit()
        return {"status": True, "filename": filename}
    else:
        # 嵌字脚本错误
        driver.quit()
        return {'status': False, "reason": res}