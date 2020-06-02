import os
import tempfile

from PIL import Image
from selenium.webdriver import Chrome
from selenium.common.exceptions import JavascriptException

from .configs import ROOT_PATH


def getPosAndText(driver: Chrome, tw_type: int) -> dict:
    with open(f"{ROOT_PATH}server\\bin\\getMainPart.js", "r", encoding="utf-8") as f:
        script = f.read()
    if tw_type == 3:
        res = driver.execute_script(script + "return getMainPartComment()")
    else:
        res = driver.execute_script(script + "return getMainPartTweet()")
    return res


def add_translation_js(driver: Chrome, processed_text: list, style: str, tw_type: int):
    with open(f"{ROOT_PATH}server\\bin\\addTranslation.js", "r", encoding="utf-8") as f:
        script = f.read()
    if tw_type == 3:
        script += "addTranslationComment(arguments)"
    else:
        script += "addTranslationMain(arguments)"
    try:
        driver.execute_script(script, processed_text, style)
        return {"error": None}
    except JavascriptException as e:
        return {"error": e.msg}


def fullscreen(driver: Chrome):
    # method copied from selenium lib
    # change to full page in headless mode to display everything
    width = driver.execute_script('return Math.max(document.body.scrollWidth, document.body.offsetWidth);')
    height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight);')
    driver.set_window_size(width, height)
    # scroll to top as the position is in the middle of the page
    driver.execute_script('window.scrollTo(document.body.scrollHeight, 0)')


def crop_screenshot(driver: Chrome, bound: list) -> str:
    (fd, filename) = tempfile.mkstemp(suffix='.png', dir=f'{ROOT_PATH}server\\cache\\')
    os.close(fd)
    driver.save_screenshot(filename)
    img: Image = Image.open(filename)
    img = img.crop(bound)
    img.save(filename)
    return filename
