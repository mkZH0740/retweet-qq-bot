# 转推机器人

从QQ操作关注推特用户的推文截图的机器人。SoreHaitACE & sudo 编写。
需要酷Q PRO实现向QQ发送图片。

能够从QQ：

1. 增加/删除对于推特用户的监听

2. 操作是否需要推特的原文，翻译，内含图片；是否需要截取转推，评论和发推

3. 实现简单的嵌字和嵌入emoji，简单改变嵌字的样式

使用run.bat自动化启动

## 注意事项

需要的python包:  
    pip install nonebot  
    pip install nonebot[scheduler]  
    pip install fastapi  
    pip install tweepy  
    pip install pillow  
    pip install selenium  

需要酷Q PRO

需要根据电脑上的Chrome版本更改server\\bin中chromedriver.exe的版本

需要自己申请twitter developer账户并创建自己的app，申请自己的百度翻译app，然后替换bot\\addon\\utils.py中对应的项目  

需要修改项目路径，分别位于bot\\addon\\utils.py和server\\services\\configs.py

请按照QQ机器人的help文档输入命令，可以直接访问fastapi提供的本地文档服务器查看服务端接口
