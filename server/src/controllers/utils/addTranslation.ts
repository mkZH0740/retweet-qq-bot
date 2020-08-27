import { replace, convert } from "twemoji";
import { PageHolder } from "./preparePage";
import { readFileSync } from "fs";


const globalTextMatcher = /{[^}]+}|[^{]+/gm;
const globalTranslationMatcher = /(#\d+ )(?!#\d+ )/gm;

const globalEmojiStyle = readFileSync(".//src//css//emoji.css", { encoding: "utf-8" });

async function preprocess(translation: string){
    // @ts-ignore
    return replace(translation, (emoji: string) => {
        return "{https://abs-0.twimg.com/emoji/v2/svg/" + convert.toCodePoint(emoji) + ".svg}";
    })
}

async function processSingleTranslation(translation: string){
    translation = await preprocess(translation);

    let rawBlocks = translation.match(globalTextMatcher);
    for (let i = 0; i < rawBlocks.length; i++){
        let currBlock = rawBlocks[i];
        if (currBlock.startsWith("{")){
            let emojiUrl = currBlock.substring(1, currBlock.length - 1);
            rawBlocks[i] = 
            `<span class="emoji-span">
                <div class="emoji-div">
                    <div class="emoji-back" style="background-image: url(${emojiUrl});"></div>
                    <img class="emoji-fore" src="${emojiUrl}">
                </div>
            </span>`;
        }else{
            rawBlocks[i] = `<span class="text">${currBlock}</span>`;
        }
    }
    return rawBlocks.join("");
}

async function solveTranslationBlock(content: string, isComment: boolean){
    let res = {};
    if (isComment){
        if (!content.startsWith("#")){
            res["1"] = await processSingleTranslation(content);
        }else{
            let seperated = content.split(globalTranslationMatcher);
            for (let i = 1; i < seperated.length; i+= 2){
                let rawIndex = seperated[i]; let rawContent = seperated[i + 1];
                let realIndex = rawIndex.substring(1, rawIndex.length - 1);
                let realContent = await processSingleTranslation(rawContent);
                res[realIndex] = realContent;
            }
        }
    }else{
        res["1"] = await processSingleTranslation(content);
    }
    return res;
}


export async function addTranslation(pageHolder: PageHolder, translation: string, cssStyle: string, tagData: string){
    const page = pageHolder.page;
    let completeCssStyle = globalEmojiStyle + cssStyle;

    let isComment = await page.evaluate(() => {
        return document.querySelector('article').firstChild.firstChild.firstChild.childNodes.length < 3;
    })
    let processedTranslation = await solveTranslationBlock(translation, isComment);

    let maxIndex = await page.$$eval("article", (elements, trans, css, tag) => {
        let styleSheet = document.createElement("style");
        styleSheet.innerHTML = css;
        document.body.appendChild(styleSheet);

        let currMax = 0;
        for (const key in trans){
            let index = parseInt(key) - 1;
            currMax = index > currMax ? index : currMax;

            let currTranslation = trans[key];
            let currArticle = elements[index];
            let textArea = currArticle.querySelector("div[lang]");
            let board = document.createElement("div"); board.className = "wrapper";

            let isMainComment = currArticle.querySelector("div[data-testid='tweet']").parentElement.childElementCount > 2;
            if (isMainComment){
                let tagBoard = document.createElement("div"); tagBoard.className = "wrapper";
                let tagImg = document.createElement("img"); tagImg.className = "tag-img"; tagImg.src = tag;
                tagBoard.appendChild(tagImg); textArea.appendChild(tagBoard);
            }

            board.innerHTML += currTranslation;
            textArea.appendChild(board);
        }
        return currMax;
    }, processedTranslation, completeCssStyle, tagData);

    return maxIndex;
}