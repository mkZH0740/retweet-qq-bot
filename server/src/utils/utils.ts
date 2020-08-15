import { convert, replace } from 'twemoji';
import { Page } from 'puppeteer-core';

export async function translateCodePoint(withCodePoint: string){
    let reg = /{\S+?}/g;
    let res = withCodePoint;
    for (let match = reg.exec(withCodePoint); match != null; match = reg.exec(withCodePoint)) {
        let code = match[0].substring(1, match[0].length - 1);
        res = res.replace(match[0], convert.fromCodePoint(code));
    }
    return res;
}

export async function translateEmoji(withEmoji: string) {
    // @ts-ignore
    return replace(withEmoji, function repl(emoji: string) {
        return "{https://abs-0.twimg.com/emoji/v2/svg/" + convert.toCodePoint(emoji) + ".svg}";
    })
}

export async function verifyPage(page: Page){
    return (await page.$$eval("article", (elements) => {return elements.length;})) > 0;
}

export async function getContent(page: Page, maxIndex: number){
    let result = await page.$$eval("article", (elements, maxPageIndex)=>{
        let boundingBox: DOMRect;
        let originalTexts = "";
        if (maxPageIndex == null){
            maxPageIndex = 128;
        }

        for (let i = 0; i < elements.length && i <= maxPageIndex; i++) {
            const element = elements[i];
            if (i == 0){
                boundingBox = element.getBoundingClientRect();
            }else{
                boundingBox.height += element.getBoundingClientRect().height;
            }

            let textArea = element.querySelector("div[lang]");
            if (textArea != null){
                originalTexts += `第${i + 1}行：`;
                let textSpans = textArea.querySelectorAll("span");
                textSpans.forEach((span) => {
                    let emojiSpan = span.querySelector("img");
                    if (emojiSpan == null){
                        originalTexts += span.innerText;
                    }else{
                        let codePoint = emojiSpan.src;
                        originalTexts += "{" + codePoint.substring(codePoint.lastIndexOf('/') + 1, codePoint.length - 4) + "}";
                    }
                });
                originalTexts += "\n";
            }

            if (element.firstChild.firstChild.firstChild.childNodes.length > 2 && maxPageIndex == 128){
                // mainpart of the page
                break;
            }
        }
        return {
            "boundingBox": {x: boundingBox.x, y: boundingBox.y, height: boundingBox.height, width: boundingBox.width},
            "originalText": originalTexts
        }
    }, maxIndex);
    return result;
}