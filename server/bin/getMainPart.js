function getMainPartBound(mainPart) {
    let loc = mainPart.getClientRects()[0]
    return [loc["left"], loc["top"], loc["right"], loc["bottom"]]
}

function getCommentPartBound(res, pos) {
    let loc_1 = res[0].getClientRects()[0]
    let loc_2 = res[pos].getClientRects()[0]
    return [loc_1["left"], loc_1["top"], loc_2["right"], loc_2["bottom"]]
}

function getMainPartTweetText(mainPart) {
    return mainPart.querySelectorAll("div[dir=auto]")[2].innerText
}

function getMainPartCommentText(res) {
    let text = ""
    for (let i = 0; i < res.length; i++) {
        text += "第" + (i+1) + "行："
        if (res[i].childElementCount < 3){
            if (res[i].querySelectorAll("div[dir=auto]")[3] !== undefined){
                text += res[i].querySelectorAll("div[dir=auto]")[3].innerText
            }
        }else{
            if (res[i].childNodes[2].childElementCount === 4){
                text += res[i].childNodes[2].childNodes[0].innerText.split("\n")[0]
            }else{
                text += res[i].childNodes[2].childNodes[1].innerText.split("\n")[0]
            }
            return text
        }
        text += "\n"
    }
}

function getMainPartComment() {
    let res = document.querySelectorAll("article>div")
    for (let i = 0; i < res.length; i++) {
        if (res[i].childElementCount > 2){
            return {
                "location": getCommentPartBound(res, i),
                "text": getMainPartCommentText(res)
            }
        }
    }
}

function getMainPartTweet() {
    let res = document.querySelectorAll("article>div")
    for (let i = 0; i < res.length; i++) {
        if (res[i].childElementCount > 2){
            return {
                "location": getMainPartBound(res[i]),
                "text": getMainPartTweetText(res[i])
            }
        }
    }
}