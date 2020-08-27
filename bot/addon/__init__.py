import requests

from nonebot import get_bot, on_command, CommandSession, scheduler
from tweepy import OAuthHandler, API, Stream

from .listener import MyListener
from .settings import SETTING
from .db_holder import databse
from .tweet_holder import Wrapper

bot = get_bot()
auth = OAuthHandler(SETTING.consumer_key, SETTING.consumer_secret)
auth.set_access_token(SETTING.access_token, SETTING.access_token_secret)
api = API(auth)
listener = MyListener(api)

stream_holder = [""]
stream_holder[0] = Stream(auth=api.auth, listener=listener)
stream_holder[0].filter(follow=listener.followed_users, is_async=True)

wrapper = Wrapper()
wrapper.load()
wrapper.run()


def get_twitter_id(screen_name: str) -> str:
    res = requests.post(url="https://tweeterid.com/ajax.php", data=f"input={screen_name.lower()}", headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}).content.decode("utf-8")
    return res


def refresh_stream():
    """
    刷新当前的tweepy流
    """
    stream_holder[0].disconnect()
    # 重取监听对象的twitter id
    listener.reload_folloed_users()
    stream_holder[0] = Stream(api.auth, listener)
    stream_holder[0].filter(follow=listener.followed_users, is_async=True)


@on_command("add", only_to_me=False)
async def add_command(session: CommandSession):
    screen_name = session.current_arg_text.strip()
    twitter_id = get_twitter_id(screen_name)
    if not twitter_id.isdigit():
        session.finish("请输入正确的screen name")
    databse.add_user(screen_name, twitter_id, str(session.event.group_id))
    refresh_stream()
    session.finish("成功！")


@on_command("delete", only_to_me=False)
async def delete_command(session: CommandSession):
    screen_name = session.current_arg_text.strip()
    databse.delete_user(screen_name, str(session.event.group_id))
    refresh_stream()
    session.finish("成功！")


@scheduler.scheduled_job('interval', seconds=60)
async def _schedule():
    curr_errlist = listener.get_all_errors()
    if len(curr_errlist) > 0:
        refresh_stream()
        await bot.send_private_msg(user_id=2267980149, message=str(curr_errlist))