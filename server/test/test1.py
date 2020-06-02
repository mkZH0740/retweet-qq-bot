import time

from selenium.webdriver import Chrome, ChromeOptions

ROOT_PATH = "C:\\Users\\mike\\Desktop\\workspace\\proj4\\src\\server\\"

option = ChromeOptions()
option.headless = True
driver = Chrome(executable_path=f"{ROOT_PATH}bin\\chromedriver.exe", options=option)
# https://mobile.twitter.com/ars_almal/status/1267158596325797894
# https://mobile.twitter.com/ars_almal/status/1267498482618654720
driver.get("https://mobile.twitter.com/rurudo_/status/1267474070590771200")
time.sleep(2)
width = driver.execute_script('return Math.max(document.body.scrollWidth, document.body.offsetWidth);')
height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight);')
driver.set_window_size(width, height)
# scroll to top as the position is in the middle of the page
driver.execute_script('window.scrollTo(document.body.scrollHeight, 0)')

with open("getMainPart.js", "r", encoding="utf-8") as f:
    script = f.read()

print(script + "return getMainPartComment()")
res = driver.execute_script(script + "return getMainPartComment()")

print(res)