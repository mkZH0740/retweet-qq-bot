'''
@author: sudo

'''
from nonebot import get_bot, scheduler, MessageSegment
from nonebot import on_command, CommandSession
from nonebot import on_request, RequestSession

from addon.utils import __A_S__,__A_T__,__c_k__,__c_s__,PROJECTPATH
from addon.utils import read_all_users, adj_group_config, get_logged_tweet, add_translation, get_screenshot, get_group_config, trans, add_user, add_to_group_log
from addon.listener import MyStreamListener
from aiocqhttp.exceptions import ActionFailed

import os, tweepy, json
bot = get_bot()
auth = tweepy.OAuthHandler(__c_k__, __c_s__)
auth.set_access_token(__A_T__, __A_S__)
api = tweepy.API(auth)
lis = MyStreamListener()
lis.build_up()
stream_holder = tweepy.Stream(api.auth, lis)
followers = read_all_users()
stream_holder.filter(follow=followers, is_async=True)
SUPPORTED_ATTRIBUTES = ['tweet', 'retweet', 'comment', 'translation', 'content']


@on_command('add', only_to_me=False)
async def add(session:CommandSession):
    buf = session.current_arg_text.split(';')
    rt = add_user(buf[0],buf[1],session.ctx['group_id'])
    if rt:
        global stream_holder
        stream_holder.disconnect()
        lis.followed_users = read_all_users()
        stream_holder = tweepy.Stream(api.auth, lis)
        stream_holder.filter(follow=followers, is_async=True)
        await session.send('成功，不需要刷新监听流')
    else:
        await session.send('失败')


@on_command('restart', only_to_me=False)
async def stream(session:CommandSession):
    global stream_holder
    stream_holder.disconnect()
    lis.followed_users = read_all_users()
    print(lis.followed_users)
    stream_holder = tweepy.Stream(api.auth, lis)
    stream_holder.filter(follow=followers, is_async=True)
    await session.send('成功')


@on_command('disable', only_to_me=False)
async def disable(session:CommandSession):
    d = dict()
    raw = session.current_arg_text.strip()
    if raw.find(';') != -1:
        k = raw.split(';')
    else:
        k = [raw]
    for each in k:
        if each in SUPPORTED_ATTRIBUTES:
            d[each] = False
    rt = adj_group_config(d, session.ctx['group_id'])
    if rt:
        await session.send('成功')
    else:
        await session.send('出错')


@on_command('enable',only_to_me=False)
async def enable(session:CommandSession):
    d = dict()
    raw = session.current_arg_text.strip()
    if raw.find(';') != -1:
        k = raw.split(';')
    else:
        k = [raw]
    for each in k:
        if each in SUPPORTED_ATTRIBUTES:
            d[each] = True
    rt = adj_group_config(d, session.ctx['group_id'])
    if rt:
        await session.send('成功')
    else:
        await session.send('出错')


@on_command('tr',only_to_me=False)
async def tr(session:CommandSession):
    if session.is_first_run:
        session.get('translation',prompt='请输入翻译文本')
    else:
        if 'index' in session.state:
            tweet = get_logged_tweet(session.state['index'],session.ctx['group_id'])
            translation = session.state['translation'].replace('\r\n','&&')
            rt = add_translation(translation,tweet['url'],tweet['tw_type'], session.ctx['group_id'])
        elif 'url' in session.state:
            translation = session.state['translation'].replace('\r\n', '&&')
            rt = add_translation(translation, session.state['url'], session.state['tw_type'], session.ctx['group_id'])
        if rt is None:
            await session.send('出错')
        else:
            await session.send(MessageSegment(type_='image', data={'file': f'file:///{rt}'}))


@tr.args_parser
async def _(session:CommandSession):
    if session.current_arg_text.isdigit():
        session.state['index'] = int(session.current_arg_text)
    else:
        if session.current_arg_text.find('twitter.com')!=-1:
            buf = session.current_arg_text.split(';')
            session.state['url'] = buf[0]
            session.state['tw_type'] = int(buf[1])


@on_command('style',only_to_me=False)
async def style(session:CommandSession):
    styles = session.current_arg_text.strip()
    if styles.find('"') != -1:
        styles = styles.replace('"', "'")
    rt = adj_group_config({'styles':styles}, session.ctx['group_id'])
    if not rt:
        await session.send('出错')
    else:
        await session.send('成功')


@on_request('group')
async def _(session: RequestSession):
    await bot.send_private_msg(2267980149,'加入群：'+str(session.ctx['group_id']))
    await session.approve()


@on_request('friend')
async def _(session: RequestSession):
    await session.approve()


@on_command('help',only_to_me=False)
async def help(session:CommandSession):
    with open(f'{PROJECTPATH}help.json','r',encoding='utf-8') as f:
        help_context = json.load(f)
    help_command = session.current_arg_text
    if help_command == '':
        await session.send(help_context['all'])
    else:
        if help_command not in help_context:
            await session.send('未知命令')
        else:
            await session.send(help_context[help_command])


@scheduler.scheduled_job('interval', seconds=60)
async def _():
    l = os.listdir(f'{PROJECTPATH}\\cache\\')
    limit = 5
    if len(l) < 5:
        limit = len(l)
    if len(lis.err_list) > 0:
        global stream_holder
        stream_holder.disconnect()
        lis.followed_users = read_all_users()
        stream_holder = tweepy.Stream(api.auth, lis)
        stream_holder.filter(follow=followers, is_async=True)
    while len(lis.err_list) > 0:
        err = lis.err_list.pop()
        await bot.send_private_msg(user_id=2267980149, message=err)
    for i in range(limit):
        filename = l.pop()
        with open(f'{PROJECTPATH}\\cache\\{filename}','r',encoding='utf-8') as f:
            tweet = json.load(f)
        buf = get_screenshot(tweet['url'],tweet['tw_type'])
        print(buf)
        if buf is None:
            print(tweet['url'] + ' not available')
            os.remove(f'{PROJECTPATH}\\cache\\{filename}')
            continue
        raw_text = buf['text']
        screenshot_path = buf['filename']
        to_send_text = f'原文：{raw_text}\n'
        try:
            for group in tweet['groups']:
                config = get_group_config(group)
                if config['translation']:
                    to_send_text += trans(raw_text) + '\n'
                if config['content'] and len(tweet['pic_urls']) > 0:
                    contents = '附件：'
                    for pic in tweet['pic_urls']:
                        contents += str(MessageSegment(type_='image',data={'file':pic}))
                    to_send_text += contents + '\n'
                index = add_to_group_log(tweet['url'],tweet['tw_type'],group)
                to_send_text += f'嵌字编号：{index}'
                await bot.send_group_msg(group_id=group, message=MessageSegment(type_='image',data={'file':f'file:///{screenshot_path}'}))
                await bot.send_group_msg(group_id=group, message=to_send_text)
                print(group)
            os.remove(screenshot_path)
            os.remove(f'{PROJECTPATH}\\cache\\{filename}')
        except ActionFailed:
            for group in tweet['groups']:
                await bot.send_group_msg(group_id=group, message= '推特被撤回或其他错误，链接：' + str(tweet['url']))
            os.remove(screenshot_path)
            os.remove(f'{PROJECTPATH}\\cache\\{filename}')
            continue
