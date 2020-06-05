function addTranslations(arguments){
    let processed_dict = arguments[0]
    let last_index = arguments[1] - 1
    let css_text = arguments[2]

    let tars = document.querySelectorAll("div[lang]")

    for (let key in processed_dict) {
        let index = parseInt(key) - 1
        let target = tars[index]

        let dummy = document.createElement("div")
        dummy.style.cssText = css_text
        dummy.lang = "zh"

        let regexp = /{\S+?}/g
        let text = processed_dict[key]
        let res = regexp.exec(text)
        while (res != null){
            let img_segment = "<img draggable=\"false\" style=\"width: 28px; height: 28px\" src=\"{}\">".replace("{}",
                "https://abs-0.twimg.com/emoji/v2/svg/" + res[0].substr(1, res[0].length - 2) + ".svg")
            text = text.replace(res[0], img_segment)
            res = regexp.exec(text)
        }
        dummy.innerHTML = text
        target.append(dummy)
    }

    // get page position
    let first_dynamic_pos = document.getElementsByTagName("article")[0].getClientRects()
    let last_dynamic_pos = document.getElementsByTagName("article")[last_index].getClientRects()

    return [first_dynamic_pos.left, first_dynamic_pos.top, last_dynamic_pos.right, last_dynamic_pos.bottom]
}
