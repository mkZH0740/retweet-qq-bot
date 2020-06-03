import time

from selenium.common.exceptions import TimeoutException, JavascriptException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait

from .configs import ROOT_PATH
from .utils import getPosAndText, fullscreen, crop_screenshot

option = ChromeOptions()
option.headless = True
option.add_argument("--disable-gpu")
driver = Chrome(executable_path=f"{ROOT_PATH}server\\bin\\chromedriver.exe", options=option)
driver.set_window_size(1080, 1920)

def get_screenshot(url: str, tw_type: int) -> dict:
    """
    Method used to get text of tweets and screenshot.
    :param url the url of the tweet
    :param tw_type the type of the tweet
    :return error: status: False, reason: reason of the error
    :return no error: status: True, text: text of the tweet, filename: screenshot file path
    """
    driver.get(url)
    try:
        WebDriverWait(driver, 8).until(lambda x: x.find_element_by_css_selector('article>div'))
    except TimeoutException:
        return {"status": False, "reason": "tweet may be deleted!"}
    time.sleep(0.5)

    fullscreen(driver)

    try:
        attrs = getPosAndText(driver, tw_type)
    except JavascriptException:
        return {"status": False, "reason": "error during executing js script!"}
    except Exception as e:
        return {"status": False, "reason": str(e)}
    bound = attrs["location"]
    text = attrs["text"]

    return {"status": True, "text": text, "filename": crop_screenshot(driver, bound)}
