import nonebot, config
from os import path
from nonebot.log import logging, logger

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(path.join(path.dirname(__file__), 'addon'), 'addon')
    logger.setLevel(logging.ERROR)
    nonebot.run()
