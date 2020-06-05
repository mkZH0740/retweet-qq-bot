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
    driver.set_window_size(1080, 1920)
    try:
        WebDriverWait(driver, 8).until(lambda x: x.find_element_by_css_selector('article>div'))
    except TimeoutException:
        driver.quit()
        return {"status": False, "reason": "tweet may be deleted!"}
    time.sleep(0.5)

    fullscreen(driver)

    if tw_type == 3:
        processed = process_multiple(translation)
    else:
        processed = process_single(translation)

    last_index = processed.pop('max')
    res = add_translation_js(driver, processed, style, last_index)

    if res is None:
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
        driver.quit()
        return {'status': False, "reason": res}