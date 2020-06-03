import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait

from .configs import ROOT_PATH
from .text_processor import process_multiple, process_single
from .utils import getPosAndText, fullscreen, crop_screenshot, add_translation_js


def logging(translation: str, processed_translation: list, style: str, url: str, tw_type: int, error: str):
    with open("err_log.txt", "a+", encoding="utf-8") as f:
        log = "\n\n"
        log += f"url: {url}; tw_type: {tw_type}\n"
        log += f"translation: {translation}\n"
        log += f"processed: {processed_translation}\n"
        log += f"style: {style}\n"
        log += f"error: {error}"
        f.write(log)


async def add_translation(translation: str, style: str, url: str, tw_type: int) -> dict:
    option = ChromeOptions()
    option.headless = True
    driver = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
    driver.get(url)
    try:
        WebDriverWait(driver, 8).until(lambda x: x.find_element_by_css_selector('article>div'))
    except TimeoutException:
        return {"status": False, "reason": "tweet may be deleted!"}
    time.sleep(0.5)

    fullscreen(driver)

    if tw_type == 3:
        processed_translation = process_multiple(translation)
        res = add_translation_js(driver, processed_translation, style, tw_type)
    else:
        processed_translation = process_single(translation)
        res = add_translation_js(driver, processed_translation, style, tw_type)
    if res["error"] is not None:
        logging(translation, processed_translation, style, url, tw_type, res["error"])
        return {"status": False, "reason": "error during executing js script!"}
    else:
        logging(translation, processed_translation, style, url, tw_type, res["error"])
    
    bound = getPosAndText(driver, tw_type)["location"]
    return {"status": True, "filename": crop_screenshot(driver, bound)}