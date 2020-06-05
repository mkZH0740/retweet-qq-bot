import time,re

from selenium.webdriver import Chrome, ChromeOptions
from server.services.text_processor import translate_twemoji_emoji, translate_emoji_twemoji
from server.services.utils import getPosAndText

ROOT_PATH = "C:\\Users\\mike\\Desktop\\workspace\\proj4\\src\\server\\"

# option = ChromeOptions()
# option.headless = True
# option.add_argument("--disable-gpu")
# driver = Chrome(executable_path=f"{ROOT_PATH}bin\\chromedriver.exe", options=option)
#
# driver.get("https://mobile.twitter.com/mkZH0740/status/1269002392302874624")
# time.sleep(2)
#
# res = getPosAndText(driver, 1)
# print(res['text'])
#
# processed_res = translate_twemoji_emoji(res['text'])
# print(processed_res)

text = "🌶是💉💧🐂🍺"
print(translate_emoji_twemoji(text))