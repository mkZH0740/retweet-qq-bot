import json


with open("settings.json", "r", encoding="utf-8") as f:
    SETTINGS = json.load(f)

print(SETTINGS)
DEBUG = True
SERVER_URL = SETTINGS['server-url']
PROJECT_PATH = SETTINGS['project-path']

LOG_PATH = f"{PROJECT_PATH}\\groups\\logs"
CONFIG_DB = f"{PROJECT_PATH}\\bin\\config.db"
TAG_PATH = f"{PROJECT_PATH}\\groups\\tags"
CSS_PATH = f"{PROJECT_PATH}\\groups\\css"
GROUP_SETTING_PATH = f"{PROJECT_PATH}\\groups"
TWEET_LOG_PATH = f"{PROJECT_PATH}\\cache"

CONSUMER_KEY = SETTINGS['twitter-api']['consumer-key']
CONSUMER_SECRET = SETTINGS['twitter-api']['consumer-secret']
ACCESS_TOKEN_KEY = SETTINGS['twitter-api']['access-token-key']
ACCESS_TOKEN_SECRET = SETTINGS['twitter-api']['access-token-secret']

BAIDU_API = SETTINGS['baidu-translation']['api']
BAIDU_SECRET = SETTINGS['baidu-translation']['secret']


EXCEPTION_MSG = "未知错误，请查看console"
SUCCEED_MSG = "成功"