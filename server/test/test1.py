import time

from selenium.webdriver import Chrome, ChromeOptions

ROOT_PATH = "C:\\Users\\mike\\Desktop\\workspace\\proj4\\src\\server\\"

option = ChromeOptions()
option.headless = True
option.add_argument("--disable-gpu")
driver = Chrome(executable_path=f"{ROOT_PATH}bin\\chromedriver.exe", options=option)
# https://mobile.twitter.com/ars_almal/status/1267158596325797894
# https://mobile.twitter.com/ars_almal/status/1267498482618654720
driver.get("https://stackoverflow.com/questions/43541925/how-to-set-the-browser-window-size-when-using-google-chrome-headless")
time.sleep(2)
width = driver.execute_script('return Math.max(document.body.scrollWidth, document.body.offsetWidth);')
height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight);')
# driver.set_window_size(width, height)
# # scroll to top as the position is in the middle of the page
# driver.execute_script('window.scrollTo(document.body.scrollHeight, 0)')

prev_window_size = driver.get_window_size()
if prev_window_size['height'] > height:
    height = prev_window_size['height']
if prev_window_size['width'] > width:
    width = prev_window_size['width']
driver.set_window_size(width, height)

driver.save_screenshot("test.png")

# with open("getMainPart.js", "r", encoding="utf-8") as f:
#     script = f.read()

# print(script + "return getMainPartComment()")
# res = driver.execute_script(script + "return getMainPartComment()")
