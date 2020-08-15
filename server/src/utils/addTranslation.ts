import{ Page } from 'puppeteer-core';
import { readFileSync } from 'fs';
import { tmpNameSync } from 'tmp';
import { preparePage } from './preparePage';
import { translateEmoji, verifyPage, getContent } from './utils';

async function solveTranslationBlock(content: string, isComment: boolean){
    let res = {};
    if (isComment) {
        let reg = /#\d+ /gm;
        let buf = content.split(reg);
        buf.shift();
        let currentIndex = 0;
        for (let match = reg.exec(content); match != null; match = reg.exec(content)) {
            res[match[0].substring(1, match[0].length - 1)] = await translateEmoji(buf[currentIndex]);
            currentIndex++;
        }
    } else {
        res = { '1': await translateEmoji(content) };
        console.log(res);
    }
    return res;
}

async function testSolve(content: string){
    let reg = /{[^}]+}/gm;
    let res = [];
    let startIndex = 0;
    for(let match = reg.exec(content); match != null; match = reg.exec(content)){
        if (match.index != startIndex)
            res.push(`<span class="text">${content.substring(startIndex, match.index)}</span>`);
        let url = match[0].substring(1, match[0].length - 1);
        let repl = 
        `<span class="outerSpan">
            <div class="firstDiv">
                <div class="secondDiv" style="background-image: url(${url});"></div>
                <img class="emoji" src="${url}">
            </div>
        </span>`
        res.push(repl);
        startIndex = match.index + match[0].length + 1;
    }
    if (startIndex != content.length - 1){
        res.push(`<span class="text">${content.substring(startIndex)}</span>`);
    }
    return res.join("");
}

export async function addTranslation(url: string, translation: string, tagPath: string, cssPath: string) {
    const pageContent = await preparePage(url);
    let result = {
        status: true,
        screenshot_path: "",
        error: ""
    }

    if (!pageContent.status){
        result.status = false; result.screenshot_path = null; result.error = pageContent.error;
    }else{
        const page: Page = pageContent.page;
        if(!verifyPage(page)){
            result.status = false; result.screenshot_path = null; result.error = "@ addTranslation => nothing on this page!";
            return result;
        }
        
        let isComment = await page.evaluate(() => {
            return document.querySelector('article').firstChild.firstChild.firstChild.childNodes.length < 3;
        })

        let processedTranslation = await solveTranslationBlock(translation, isComment);

        let binaryData = readFileSync(tagPath);
        let base64Str = binaryData.toString('base64');
        let basicTagData = 'data:image/png;base64,' + base64Str;

        const basicEmojiStyle = readFileSync(".//src//css//emoji.css").toString("utf-8");
        const groupTextStyle = readFileSync(cssPath).toString("utf-8");

        let maxIndex = await page.$$eval("article", (elements, textBlock, textStyle, emojiStyle, tagData) => {
            let emojiURLMatcher = /{[^}]+}/gm;
            let styleSheet = document.createElement("style");
            styleSheet.innerHTML = emojiStyle + textStyle;
            document.body.appendChild(styleSheet);
            let maxPageIndex = 0;

            for (const key in textBlock){
                let index = parseInt(key) - 1;
                let currArticle = elements[index];
                console.log(index)
                console.log(currArticle);
                let currTranslation = textBlock[key];

                let board = document.createElement("div"); board.style.paddingBottom = "0px"; board.style.marginBottom = "0px";

                let seperate = [];
                let startIndex = 0;
                for(let match = emojiURLMatcher.exec(currTranslation); match != null; match = emojiURLMatcher.exec(currTranslation)){
                    if (match.index != startIndex)
                        seperate.push(`<span class="text">${currTranslation.substring(startIndex, match.index)}</span>`);
                    let emojiUrl = match[0].substring(1, match[0].length - 1);
                    let repl = 
                    `<span class="outerSpan">
                        <div class="firstDiv">
                            <div class="secondDiv" style="background-image: url(${emojiUrl});"></div>
                            <img class="emoji" src="${emojiUrl}">
                        </div>
                    </span>`
                    seperate.push(repl);
                    startIndex = match.index + match[0].length;
                }
                if (startIndex != currTranslation.length - 1)
                    seperate.push(`<span class="text">${currTranslation.substring(startIndex)}</span>`);
                
                let rawHtml = seperate.join("");
                console.log(currArticle.firstChild.firstChild.firstChild.childNodes.length);
                if (currArticle.firstChild.firstChild.firstChild.childNodes.length > 2) {
                    let wrapper = document.createElement("div");
                    let tag = document.createElement("img"); tag.src = tagData; tag.style.height = "28px";
                    wrapper.appendChild(tag);
                    currArticle.querySelector("div[lang]").appendChild(wrapper);
                }
                board.innerHTML += rawHtml;
                currArticle.querySelector("div[lang]").appendChild(board);
                if (index > maxPageIndex){
                    maxPageIndex = index;
                }
            }
            return maxPageIndex;
        }, processedTranslation, groupTextStyle, basicEmojiStyle, basicTagData);
        maxIndex = (maxIndex == 0)? null : maxIndex;

        let content = await getContent(page, maxIndex);
        let screenshotPath = tmpNameSync({ postfix: '.png', tmpdir: './/src//cache' });
        try{
            await page.screenshot({ path: screenshotPath, clip: content.boundingBox });
            result.screenshot_path = screenshotPath;
        }catch(error){
            result.status = false; result.screenshot_path = null; result.error = "@ addTranslation => screenshot error!"
        }finally{
            await page.browser().close();
        }
    }
    return result;
}