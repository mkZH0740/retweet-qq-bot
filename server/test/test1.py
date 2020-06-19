import requests

server = "http://127.0.0.1:8000"

data = {
    "url": "https://twitter.com/natsuiromatsuri/status/1272210188871712769",
    "style": "font-family: 黑体;font-size: 28px;color: yellow",
    "tag": "C:\\Users\\mike\\WebstormProjects\\server\\pics\\wheel.png",
    "translation": "#1 测试🏮\n#2 我有一句话一定要说！❄❄\n",
    "code": 1
}
res = requests.post(f"{server}/translation", json=data)
print(res.content.decode("utf-8"))

