import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait

from .configs import ROOT_PATH
from .utils import getPosAndText, fullscreen, crop_screenshot
from .text_processor import translate_twemoji_emoji


async def get_screenshot(url: str, tw_type: int) -> dict:
    """
    :param url: 推特URL
    :param tw_type: 推特类型代码
    :return: 运行不成功的status和reason，或者成功的status，截图名称filename和推特内文字
    """

    # 为每个任务启动一个headless chrome
    option = ChromeOptions()
    option.headless = True
    option.add_argument("--disable-gpu")
    driver = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
    # 设置默认窗口大小为1920x1080
    driver.set_window_size(1920, 1080)

    driver.get(url)

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

    # 尝试获取推文内容在页面上的位置和内部的文本
    attrs = getPosAndText(driver, tw_type)
    if 'error' in attrs:
        # 获取失败
        driver.quit()
        return {"status": False, "reason": attrs["error"]}

    position: dict = attrs["position"]
    text: str = attrs["text"]
    bound = (position['left'], position['top'], position['right'], position['bottom'])

    # 获取整个页面的截图，然后切割出推文内容的部分
    filename = crop_screenshot(driver, bound)
    driver.quit()
    # 将推文文本中的twemoji code转化为emoji
    text = translate_twemoji_emoji(text)
    return {"status": True, "text": text, "filename": filename}
