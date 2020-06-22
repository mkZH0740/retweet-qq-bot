import json


with open("settings.json", "r", encoding="utf-8") as f:
    SETTINGS = json.load(f)


SERVER_URL = SETTINGS['server-url']
PROJECT_PATH = SETTINGS['project-path']
GROUP_LOG_PATH = f"{PROJECT_PATH}\\bin\\logs.db"
CONFIG_LOG_PATH = f"{PROJECT_PATH}\\bin\\config.db"
GROUP_SETTING_PATH = f"{PROJECT_PATH}\\groups"
SCREENSHOT_PATH = f"{PROJECT_PATH}\\cache"
TWEET_LOG_PATH = f"{PROJECT_PATH}\\cache"

CONSUMER_KEY = SETTINGS['twitter-api']['consumer-key']
CONSUMER_SECRET = SETTINGS['twitter-api']['consumer-secret']
ACCESS_TOKEN_KEY = SETTINGS['twitter-api']['access-token-key']
ACCESS_TOKEN_SECRET = SETTINGS['twitter-api']['access-token-secret']

BAIDU_API = SETTINGS['baidu-translation']['api']
BAIDU_SECRET = SETTINGS['baidu-translation']['secret']