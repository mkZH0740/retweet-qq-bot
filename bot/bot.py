import nonebot, config
from os import path
from nonebot.log import logging, logger

if __name__ == '__main__':
    # 启动bot
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(path.join(path.dirname(__file__), 'addon'), 'addon')
    nonebot.run()
