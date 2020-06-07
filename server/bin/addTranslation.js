/*
 * javascript function to add translation block onto twitter page
 * @author: sudo
 */
function addTranslations(arguments){
    // 处理过后的文本字典
    let processed_dict = arguments[0]
    // 最后一个推文的序号（从0开始）
    let last_index = arguments[1] - 1
    // 文本css样式
    let css_text = arguments[2]

    // 推特的推文被带有lang标签的div包裹，用querySelectorAll方法找到所有推文div
    let tars = document.querySelectorAll("div[lang]")

    for (let key in processed_dict) {
        // 多行文本对应序号（从0开始）
        let index = parseInt(key) - 1
        // 对应的推文div
        let target = tars[index]

        // 创建容纳翻译的div
        let dummy = document.createElement("div")
        // 设置css样式
        dummy.style.cssText = css_text
        // 翻译lang为简体中文
        dummy.lang = "zh"

        // twemoji由{}包裹，用regExp找到所有
        let regexp = /{\S+?}/g
        // 文本
        let text = processed_dict[key]
        let res = regexp.exec(text)
        // 遍历整个文本，知道找不到下一个twemoji
        while (res != null){
            // 硬编码twemoji的img元素，twemoji的图片库为https://abs-0.twimg.com/emoji/v2/svg/*.svg
            let img_segment = "<img draggable=\"false\" style=\"width: 28px; height: 28px\" src=\"{}\">".replace("{}",
                "https://abs-0.twimg.com/emoji/v2/svg/" + res[0].substr(1, res[0].length - 2) + ".svg")
            // 将twemoji替换为其img元素
            text = text.replace(res[0], img_segment)
            // 获取下一个位置
            res = regexp.exec(text)
        }
        // 加入内容
        dummy.innerHTML = text
        // 将容纳翻译的div加入目标推文div的子元素，显示在推文文本的正下方
        target.append(dummy)
    }

    // get page position
    let first_dynamic_pos = document.getElementsByTagName("article")[0].getClientRects()
    let last_dynamic_pos = document.getElementsByTagName("article")[last_index].getClientRects()

    return [first_dynamic_pos.left, first_dynamic_pos.top, last_dynamic_pos.right, last_dynamic_pos.bottom]
}
