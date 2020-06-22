from .databaseHelper import DBManager
from nonebot import on_command, CommandSession
from sqlite3 import DatabaseError


manager = DBManager()


def produceValidSettings(rawSettingStr: str, setTo: bool):
    if rawSettingStr.find(";") != -1:
        commands = rawSettingStr.split(";")
    else:
        commands = [rawSettingStr]
    validCommands = {}
    for command in commands:
        if command in manager.default_group_setting.keys():
            validCommands[command] = setTo
    if len(validCommands.keys()) < 0:
        return None
    return validCommands


@on_command("enable", aliases='e', only_to_me=False)
async def commandEnable(session: CommandSession):
    validCommands = produceValidSettings(session.current_arg_text.strip(), True)
    if validCommands is None:
        session.finish(message="请输入支持的参数！")
        return
    try:
        manager.adjust_group_settings(group_id=session.event.group_id, 
            adjusted_value=validCommands)
    except DatabaseError:
        await session.send("数据库错误！")


@on_command("disable", aliases='d', only_to_me=False)
async def commandDisable(session: CommandSession):
    validCommands = produceValidSettings(session.current_arg_text.strip(), False)
    if validCommands is None:
        session.finish(message="请输入支持的参数！")
        return
    try:
        manager.adjust_group_settings(group_id=session.event.group_id, 
            adjusted_value=validCommands)
    except DatabaseError:
        await session.send("数据库错误！")


@on_command("add", aliases='a', only_to_me=False)
async def commandAdduser(session: CommandSession):
    try:
        screen_name, user_id = session.current_arg_text.strip().split(";");
    except ValueError:
        session.finish(message="参数数量错误！")
    if screen_name.isdigit():
        session.finish("screen name不能为数字！")
    if not user_id.isdigit():
        session.finish("user id必须为数字！")
    try:
        manager.add_user(screen_name=screen_name, user_id=user_id, 
            group_id=session.event.group_id)
    except DatabaseError:
        session.finish("数据库错误！")


@on_command("style", only_to_me=False)
async def commandEditStyle(session: CommandSession):
    styleText = session.current_arg_text.strip()
    manager.adjust_group_settings(group_id=session.event.group_id, adjusted_value={"css-text": styleText})
    await session.send("成功")
    
