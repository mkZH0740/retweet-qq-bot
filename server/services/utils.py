import os
import tempfile

from PIL import Image
from selenium.webdriver import Chrome
from selenium.common.exceptions import JavascriptException

from .configs import ROOT_PATH


def getPosAndText(driver: Chrome, tw_type: int) -> dict:
    with open(f"{ROOT_PATH}server\\bin\\getMainPart.js", "r", encoding="utf-8") as f:
        script = f.read()
    script += "return getMainPart();"
    try:
        return driver.execute_script(script, tw_type)
    except JavascriptException as e:
        return {'error': e.msg}


def add_translation_js(driver: Chrome, processed_dict: dict, style: str, last_index: int):
    with open(f"{ROOT_PATH}server\\bin\\addTranslation.js", "r", encoding="utf-8") as f:
        script = f.read()
    script += "addTranslations(arguments);"
    try:
        driver.execute_script(script, processed_dict, last_index, style)
        return None
    except JavascriptException as e:
        return e.msg


def fullscreen(driver: Chrome):
    # method copied from selenium lib
    # change to full page in headless mode to display everything
    width = driver.execute_script('return Math.max(document.body.scrollWidth, document.body.offsetWidth);')
    height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight);')
    previous_width = driver.get_window_size()['width']
    previous_height = driver.get_window_size()['height']

    width = max(width, previous_width)
    height = max(height, previous_height)

    driver.set_window_size(width, height)
    # scroll to top as the position is in the middle of the page
    driver.execute_script('window.scrollTo(document.body.scrollHeight, 0)')


def crop_screenshot(driver: Chrome, bound) -> str:
    (fd, filename) = tempfile.mkstemp(suffix='.png', dir=f'{ROOT_PATH}server\\cache\\')
    os.close(fd)
    driver.save_screenshot(filename)
    img: Image = Image.open(filename)
    img = img.crop(bound)
    img.save(filename)
    return filename


'''
{'1': 'img draggable="false" class="emoji" alt="�" src="https://twemoji.maxcdn.com/v/13.0.0/72x72/1f3ee.png">那<img draggable="false" class="emoji" alt="�" src="https://twemoji.maxcdn.com/v/13.0.0/72x72/1f489.p
ng"><img draggable="false" class="emoji" alt="�" src="https://twemoji.maxcdn.com/v/13.0.0/72x72/1f4a7.png">牛<img draggable="false" class="emoji" alt="�" src="https://twemoji.maxcdn.com/v/13.0.0/72x72/1f37a.png
"'}

'''