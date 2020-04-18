import requests, json

# 1, 测试截图
# d = {
#     "url": "https://mobile.twitter.com/shirakamifubuki/status/1239361624533655552",
#     "tw_type": 1
# }
# res = requests.post('http://127.0.0.1:8000/screenshot', json=d)
# buf = json.loads(res.content.decode('utf-8'))
# print(buf)
# response: {'filename': 'C:\\Users\\mike\\PycharmProjects\\fastapiServer\\cache\\5nt1h115.png', 'text': 'おはこーん\n(^・ω・^§)ﾉ'}

#2, 测试加入设置
# d = {
#     "tweet": False,
#     "retweet": False,
#     "styles": 'font-size:25px, font-family:"微软雅黑", color: orange'
# }
# res = requests.post('http://127.0.0.1:8000/adb/2267980149', json=d)
# print(res.content.decode('utf-8'))

#3, 测试读取设置
# res = requests.get('http://127.0.0.1:8000/rdb/2267980149')
# print(json.loads(res.content.decode('utf-8')))
# response: {'tweet': False, 'retweet': False, 'comment': True, 'translation': True, 'content': True, 'styles': 'font-size:25px, font-family:"微软雅黑", color: orange'}

#4, 测试读取所有用户
# res = requests.get('http://127.0.0.1:8000/all')
# print(json.loads(res.content.decode('utf-8')))
# response: List[int]

#5, 测试加入新用户
# d = {
#     "user_id": 1026033963603714048,
#     "screen_name": "hukkatunoyuyuta"
# }
# res = requests.post('http://127.0.0.1:8000/adduser/981045', json=d)
# print(res.content.decode('utf-8'))

#6, 读取监听群
# res = requests.get('http://127.0.0.1:8000/readuser/hukkatunoyuyuta')
# print(json.loads(res.content.decode('utf-8')))
# response: [2267980149, 981045]

#7, 读取缓存的log
# res = requests.get('http://127.0.0.1:8000/rldb/2/20')
# print(res.content.decode('utf-8'))
# response {"url":"https://mobile.twitter.com/amamiya_kokoro/status/1233265537649528832","tw_type":1}

#8, 加入新的缓存log
# d = {
#     "url": "https://mobile.twitter.com/hukkatunoyuyuta/status/1239206235871662081",
#     "tw_type": 1
# }
# res = requests.post('http://127.0.0.1:8000/aldb/2267980149', json=d)
# print(res.content.decode('utf-8'))
#response {"index":"1"}

#9, 测试嵌字
# d = {
#     "url": "https://mobile.twitter.com/hukkatunoyuyuta/status/1239206235871662081",
#     "tw_type": 1,
#     "group_id": 2267980149,
#     "translation": "为什么？"
# }
# res = requests.post('http://127.0.0.1:8000/add_translation', json=d)
# print(json.loads(res.content.decode('utf-8')))
# response: {'filepath': 'C:\\Users\\mike\\PycharmProjects\\fastapiServer\\cache\\i1rgb9qh.png'}