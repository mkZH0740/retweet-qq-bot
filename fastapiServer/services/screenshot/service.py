from fastapi import APIRouter
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from services.config import ROOTPATH
from pydantic import BaseModel
import time

router = APIRouter()


class ScreenshotTweet(BaseModel):
    url:str
    tw_type:int


@router.post('/screenshot')
def get_screenshot(tweet:ScreenshotTweet):
    browser = Browser('chrome', executable_path=f'{ROOTPATH}bin\\chromedriver.exe', headless=True)
    browser.visit(tweet.url)
    if not browser.is_element_present_by_tag('article', wait_time=8):
        browser.quit()
        return {'status': False}
    time.sleep(1)
    text = ''
    if tweet.tw_type != 3:
        try:
            text = browser.find_by_tag('article').first.find_by_css('div[lang]').first['innerText']
        except ElementDoesNotExist:  # No text presented in article
            pass
        finally:
            filename = browser.find_by_tag('article').first.screenshot(f'{ROOTPATH}cache\\', full=True)
    else:
        browser.full_screen()
        dynamics = browser.find_by_tag('article')
        limit = int(browser.execute_script("return document.getElementsByTagName('article').length"))
        print(limit)
        if limit > 8:
            last_index = len(dynamics) - 1
            count = browser.execute_script(f"return document.getElementsByTagName('article')[{last_index}].childNodes[0].childNodes[0].childNodes.length")
            if int(count) == 3:
                filename = browser.find_by_tag('article')[last_index].screenshot(f'{ROOTPATH}cache\\')
                try:
                    text = dynamics[last_index].find_by_css('div[lang]').first['innerText'] + '\n'
                except ElementDoesNotExist:
                    text = ''
                browser.quit()
                print('too long: last_index')
                return {'filename': filename, 'text': text}
            else:
                for i in range(len(dynamics)):
                    count = browser.execute_script(f"return document.getElementsByTagName('article')[{i}].childNodes[0].childNodes[0].childNodes.length")
                    if int(count) == 3:
                        filename = browser.find_by_tag('article')[last_index].screenshot(f'{ROOTPATH}cache\\')
                        try:
                            text = dynamics[i].find_by_css('div[lang]').first['innerText'] + '\n'
                        except ElementDoesNotExist:
                            text = ''
                        browser.quit()
                        print('too long: find in list')
                        return {'filename': filename, 'text': text}
        for i in range(len(dynamics)):
            try:
                text += f'第{i+1}行' + dynamics[i].find_by_css('div[lang]').first['innerText'] + '\n'
            except ElementDoesNotExist:  # No text presented in article
                pass
            finally:
                filename = browser.find_by_tag('section').first.screenshot(f'{ROOTPATH}cache\\', full=True)
    browser.quit()
    return {'filename': filename, 'text': text}
