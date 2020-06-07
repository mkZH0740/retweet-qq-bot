/*
 * javascript function to get tweet part position on screen and tweet text content
 * @author: sudo
 */
function getMainPart(arguments) {
    // 推特类型代码
    let tw_type = arguments[0]
    let text = ""
    let pos = {
        "left": 0,
        "top": 0,
        "right": 0,
        "bottom": 0
    }
    // 获取所有推文article元素
    let targets = document.getElementsByTagName("article")
    if (tw_type !== 3){
        // 不是评论推文，只关心第一个，也就是主推文
        let target = targets[0].querySelector("div[lang]")
        if (target != null){
            // 获取文本
            for (let i = 0; i < target.childNodes.length; i++) {
                if (target.childNodes[i].getElementsByTagName("img").length !== 0) {
                    // 存在img标签，是twemoji
                    let emoji_url = target.childNodes[i].getElementsByTagName("img")[0].src
                    let codePoint = emoji_url.substring(emoji_url.lastIndexOf("/") + 1, emoji_url.lastIndexOf("."))
                    text += "{" + codePoint + "}"
                } else {
                    text += target.childNodes[i].innerText
                }
            }
        }
        pos["left"] = targets[0].getClientRects()[0].left
        pos["top"] = targets[0].getClientRects()[0].top
        pos["right"] = targets[0].getClientRects()[0].right
        pos["bottom"] = targets[0].getClientRects()[0].bottom
    }else{
        // 是评论推文，关心当前推文和之前所有的对话内容
        // 记录是否到达当前推文
        let foundMainPart = false
        for (let i = 0; !foundMainPart; i++) {
            // 当前对话中没有文本
            if (targets[i].querySelector("div[lang]") == null){
                continue
            }
            // 记录当前行数
            text += "第" + (i+1) + "行："
            for (let j = 0; j < targets[i].querySelector("div[lang]").childNodes.length; j++) {
                if (targets[i].querySelector("div[lang]").childNodes[j].getElementsByTagName("img").length !== 0){
                    // 存在img标签，是twemoji
                    let emoji_url = targets[i].querySelector("div[lang]").childNodes[j].getElementsByTagName("img")[0].src
                    let codePoint = emoji_url.substring(emoji_url.lastIndexOf("/") + 1, emoji_url.lastIndexOf("."))
                    text += "{" + codePoint + "}"
                }else{
                    text += targets[i].querySelector("div[lang]").childNodes[j].innerText
                }
            }
            if (targets[i].firstChild.childNodes.length > 2){
                // 当前推文是评论对话中唯一一个第一个子元素的子元素数量超过2的推文，因此找到了当前推文
                foundMainPart = true
                pos["left"] = targets[0].getClientRects()[0].left
                pos["top"] = targets[0].getClientRects()[0].top
                pos["right"] = targets[i].getClientRects()[0].right
                pos["bottom"] = targets[i].getClientRects()[0].bottom
            }else{
                // 没找到当前推文，换行
                text += "\n"
            }
        }
    }
    return {"position": pos, "text": text}
}