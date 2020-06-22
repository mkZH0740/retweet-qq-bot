# 转推机器人

从QQ操作关注推特用户的推文截图的机器人。SoreHaitACE & sudo 编写。
需要酷Q PRO实现向QQ发送图片。

能够从QQ：

1. 增加/删除对于推特用户的监听

2. 操作是否需要推特的原文，翻译，内含图片；是否需要截取转推，评论和发推

3. 实现简单的嵌字和嵌入emoji，简单改变嵌字的样式

## 注意事项

需要的python包:  
    pip install nonebot  
    pip install nonebot[scheduler]  
    pip install tweepy  

需要的npm包:  
    npm i twemoji  
    npm i express  
    npm i puppeteer  
    npm i tmp

需要酷Q PRO

需要自己申请twitter developer账户并创建自己的app，申请自己的百度翻译app，然后替换bot\\settings.json中对应的项目  

需要修改项目路径，位于bot\\settings.json  

如果需要修改截图服务器地址和端口，也位于bot\\settings.json

请按照QQ机器人的help文档输入命令
