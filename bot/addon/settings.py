import json


class Settings:
    """
    该类保存bot运行的所有设置
    """
    debug = True

    server_url: str
    project_path: str

    group_log_path: str
    config_path: str
    group_tag_path: str
    group_css_path: str
    group_setting_path: str
    tweet_log_path: str

    consumer_key: str
    consumer_secret: str
    access_token: str
    access_token_secret: str

    baidu_api: str
    baidu_secret: str

    def __init__(self):
        with open("settings.json", "r", encoding="utf-8") as f:
            raw_settings = json.load(f)

        self.server_url = raw_settings["server-url"]
        self.project_path = raw_settings["project-path"]

        self.group_log_path = f"{self.project_path}\\groups\\logs"
        self.config_path = f"{self.project_path}\\bin\\config.db"
        self.group_tag_path = f"{self.project_path}\\groups\\tags"
        self.group_css_path = f"{self.project_path}\\groups\\css"
        self.group_setting_path = f"{self.project_path}\\groups\\settings"
        self.tweet_log_path = f"{self.project_path}\\cache"

        self.consumer_key = raw_settings["twitter-api"]["consumer-key"]
        self.consumer_secret = raw_settings["twitter-api"]["consumer-secret"]
        self.access_token = raw_settings["twitter-api"]["access-token"]
        self.access_token_secret = raw_settings["twitter-api"]["access-token-secret"]

        self.baidu_api = raw_settings['baidu-translation']['api']
        self.baidu_secret = raw_settings['baidu-translation']['secret']


# 全局设置代理
SETTING = Settings()
