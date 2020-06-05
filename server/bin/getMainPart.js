function getMainPart() {
    let tw_type = arguments[0]
    let text = ""
    let pos = {
        "left": 0,
        "top": 0,
        "right": 0,
        "bottom": 0
    }

    let targets = document.getElementsByTagName("article")
    if (tw_type !== 3){
        let target = targets[0].querySelector("div[lang]")
        for (let i = 0; i < target.childNodes.length; i++) {
            if (target.childNodes[i].getElementsByTagName("img").length !== 0){
                // img
                let emoji_url = target.childNodes[i].getElementsByTagName("img")[0].src
                let codePoint = emoji_url.substring(emoji_url.lastIndexOf("/") + 1, emoji_url.lastIndexOf("."))
                text += "{" + codePoint + "}"
            }else{
                text += target.childNodes[i].innerText
            }
        }
        pos["left"] = targets[0].getClientRects()[0].left
        pos["top"] = targets[0].getClientRects()[0].top
        pos["right"] = targets[0].getClientRects()[0].right
        pos["bottom"] = targets[0].getClientRects()[0].bottom
    }else{
        let foundMainPart = false
        for (let i = 0; !foundMainPart; i++) {
            text += "第" + (i+1) + "行："
            for (let j = 0; j < targets[i].querySelector("div[lang]").childNodes.length; j++) {
                if (targets[i].querySelector("div[lang]").childNodes[j].getElementsByTagName("img").length !== 0){
                    // img
                    let emoji_url = targets[i].querySelector("div[lang]").childNodes[j].getElementsByTagName("img")[0].src
                    let codePoint = emoji_url.substring(emoji_url.lastIndexOf("/") + 1, emoji_url.lastIndexOf("."))
                    text += "{emoji: " + codePoint + "}"
                }else{
                    text += targets[i].querySelector("div[lang]").childNodes[j].innerText
                }
            }
            if (targets[i].firstChild.childNodes.length > 2){
                foundMainPart = true
                pos["left"] = targets[0].getClientRects()[0].left
                pos["top"] = targets[0].getClientRects()[0].top
                pos["right"] = targets[i].getClientRects()[0].right
                pos["bottom"] = targets[i].getClientRects()[0].bottom
            }else{
                text += "\n"
            }
        }
    }
    return {"position": pos, "text": text}
}