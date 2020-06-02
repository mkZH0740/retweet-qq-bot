//let arguments = [[['#1 ', ['小祭二周年快乐！', '{emj}1f3ee']], ['#2 ', ['哇！可爱！爱了！']]], "font-family:黑体;font-size:28px;color:black"]
function addTranslationComment(arguments) {
    // arguments[0] [['#1 ', ['小祭二周年快乐！', '{emj}1f3ee']], ['#2 ', ['哇！可爱！爱了！']]]
    let res = document.querySelectorAll("article>div")
    for (let i = 0; i < arguments[0].length; i++) {
        let index = parseInt(arguments[0][i][0].substring(1, arguments[0][i][0].length - 1)) - 1
        let holder = document.createElement("span")
        for (let j = 0; j < arguments[0][i][1].length; j++) {
            if (arguments[0][i][1][j].startsWith("{emj}")){
                let emj_segment = document.createElement("img")
                emj_segment.src = "https://abs-0.twimg.com/emoji/v2/svg/" + arguments[0][i][1][j].substring(5) + ".svg"
                emj_segment.style.height = "28px"
                emj_segment.style.width = "28px"
                holder.append(emj_segment)
            }else{
                let text_segment = document.createElement("span")
                text_segment.innerText = "\n" + arguments[0][i][1][j].replace(/&&/g,"\n")
                text_segment.lang = "zh"
                text_segment.style.cssText = arguments[1]
                holder.append(text_segment)
            }
        }

        if (res[index].childElementCount > 2){
            if (res[index].childNodes[2].childElementCount <= 4){
                let tar = res[index].childNodes[2].childNodes[0].childNodes[0]
                tar.append(holder)
            }else{
                let tar = res[index].childNodes[2].childNodes[1].childNodes[0]
                tar.append(holder)
            }
        }else{
            if (res[index].querySelectorAll("div[dir=auto]")[3] !== undefined){
                res[index].querySelectorAll("div[dir=auto]")[3].append(holder)
            }
        }
    }
}


function addTranslationMain(arguments) {
    let res = document.querySelectorAll("article>div")[0]
    let holder = document.createElement("span")
    for (let i = 0; i < arguments[0].length; i++) {
        if (arguments[0][i].startsWith("{emj}")){
            let emj_segment = document.createElement("img")
            emj_segment.src = "https://abs-0.twimg.com/emoji/v2/svg/" + arguments[0][i].substring(5) + ".svg"
            emj_segment.style.height = "28px"
            emj_segment.style.width = "28px"
            holder.append(emj_segment)
        }else{
            let text_segment = document.createElement("span")
            text_segment.innerText = "\n" + arguments[0][i].replace(/&&/g,"\n")
            text_segment.lang = "zh"
            text_segment.style.cssText = arguments[1]
            holder.append(text_segment)
        }
    }

    if (res.childNodes[2].childElementCount <= 4){
        let tar = res.childNodes[2].childNodes[0].childNodes[0]
        tar.append(holder)
    }else{
        let tar = res.childNodes[2].childNodes[1].childNodes[0]
        tar.append(holder)
    }
}