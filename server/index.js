const express = require('express');
const puppeteer = require('puppeteer');
const twemoji = require('twemoji');
const tmp = require('tmp');
const fs = require('fs');

const app = express();
app.use(express.json());


async function prepare(url) {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url);
    let res = await page.waitForSelector('div[lang]', {timeout: 5000}).catch((err) => {
        console.log(err);
        return null;
    });
    if (res == null){
        await browser.close();
        return null;
    }

    let maxViewPort = await page.evaluate(() => {
        return {
            height: Math.max(document.body.scrollHeight, document.body.offsetHeight),
            width: Math.max(document.body.scrollWidth, document.body.offsetWidth)
        }
    });
    await page.setViewport(maxViewPort);
    return page
}


async function parseTwemoji(content){
    let reg = /{\S+?}/g;
    let match = reg.exec(content);
    let need_replace = []
    while (match != null){
        need_replace.push(match[0]);
        match = reg.exec(content);
    }
    need_replace.forEach(element => {
        let codePoint = element.substring(1, element.length - 1);
        let emoji = twemoji.convert.fromCodePoint(codePoint);
        content = content.replace(element, emoji);
    });
    return content;
}


async function takeScreenshot(page, maxIndex){
    let result = await page.evaluate(function getInfo(maxIndex) {
        let currBoundingBox = {x: 0, y: 0, height: 0, width: 0};
        let currText = "";
        let elements = document.querySelectorAll('article');

        for (let i = 0; i <= maxIndex; i++) {
            if (i === 0){
                currBoundingBox = elements[i].getBoundingClientRect();
            }else{
                currBoundingBox.height += elements[i].getBoundingClientRect().height;
            }

            let currTextHolder = elements[i].querySelector('div[lang]')
            if (currTextHolder != null){
                if (maxIndex !== 0){
                    currText += `第${i + 1}行：`
                }

                let allTextSpan = currTextHolder.querySelectorAll('span');
                for (let j = 0; j < allTextSpan.length; j++) {
                    let emojiSegment = allTextSpan[j].querySelector('img');
                    if (emojiSegment != null){
                        let codePoint = emojiSegment.src;
                        codePoint = codePoint.substring(codePoint.lastIndexOf('/') + 1, codePoint.length - 4);
                        currText += `{${codePoint}}`;
                    }else{
                        currText += allTextSpan[j].innerText;
                    }
                }

                if (i !== maxIndex) {
                    currText += "\n";
                }
            }
        }

        return {
            properBoundingBox: {x: currBoundingBox.x, y: currBoundingBox.y, height: currBoundingBox.height, width: currBoundingBox.width},
            text: currText
        }
    }, maxIndex)

    let screenshotPath = tmp.tmpNameSync({postfix: ".png", tmpdir: ".//cache"});
    console.log(screenshotPath);

    await page.screenshot({
        path: screenshotPath,
        clip: result.properBoundingBox
    })

    result.text = await parseTwemoji(result.text);

    return {
        status: true,
        screenshotPath: screenshotPath,
        rawText: result.text
    }
}


app.post('/screenshot', (req, res) => {
    (async () => {
        const page = await prepare(req.body['url'])
        if (page == null){
            res.send({status: false, reason: "Prepare=>Timeout Err: Possible deleted tweet!"});
        }else {
            let maxIndex = 0;

            if (req.body['code'] === 3) {
                maxIndex = await page.$$eval('article', (elements) => {
                    for (let i = 0; i < elements.length; i++) {
                        if (elements[i].firstChild.childNodes.length > 2) {
                            return i;
                        }
                    }
                })
            }

            let result = await takeScreenshot(page, maxIndex);
            await page.browser().close()
            res.send(result);
        }
    })()
})


async function parseEmoji(content){
    return twemoji.replace(content, (emoji) => {
        let codePoint = twemoji.convert.toCodePoint(emoji);
        return `{${codePoint}}`
    });
}


async function solveTranslation(content){
    let reg = /(#\d+ )(\S+)/g;
    let match = reg.exec(content);
    let result = {};
    while(match != null){
        let indexSegment = match[1];
        indexSegment = indexSegment.substring(1, indexSegment.length - 1);
        let translationSegment = match[2];
        translationSegment = await parseEmoji(translationSegment);
        result[indexSegment] = translationSegment;
        match = reg.exec(content);
    }
    return result;
}


app.post('/translation', (req, res) => {
    (async () => {
        const page = await prepare(req.body['url']);
        if (page == null){
            res.send({status: false, reason: "Prepare=>Timeout Err: Possible deleted tweet!"});
        }else {
            let tagPath = req.body['tag'];
            let style = req.body['style'];
            let translation = {};

            let binaryData = fs.readFileSync(tagPath);
            let base64Str = binaryData.toString('base64');
            let dataURI = 'data:image/png;base64,' + base64Str;

            let maxIndex = 0;

            if (req.body['code'] === 3) {
                translation = await solveTranslation(req.body['translation']);
                for (const key in translation) {
                    let index = parseInt(key) - 1;
                    if (index > maxIndex) {
                        maxIndex = index;
                    }
                }

                await page.$$eval('div[lang]', (elements, tagData, translation, style) => {
                    let reg = /{\S+?}/g;

                    for (const key in translation) {
                        let index = parseInt(key) - 1;
                        let currTranslation = translation[key];
                        let match = reg.exec(currTranslation);
                        let previousIndex = 0;
                        let holder = document.createElement('div');
                        holder.lang = "zh";
                        let target = elements[index];

                        while (match != null) {
                            if (match.index > previousIndex) {
                                let content = currTranslation.substring(previousIndex, match.index);
                                let textSegment = document.createElement('span');
                                textSegment.innerText = content;
                                textSegment.style.cssText = style;
                                holder.appendChild(textSegment);
                            }
                            let codePoint = match[0].substring(1, match[0].length - 1);
                            let imgSegment = document.createElement('span');
                            let emojiHolder = document.createElement('img');
                            emojiHolder.src = `https://abs-0.twimg.com/emoji/v2/svg/${codePoint}.svg`;
                            emojiHolder.style.height = "28px";
                            emojiHolder.style.width = "28px";
                            imgSegment.appendChild(emojiHolder);
                            holder.appendChild(imgSegment);

                            previousIndex = match.index + match[0].length;
                            match = reg.exec(currTranslation);
                        }

                        if (previousIndex !== currTranslation.length - 1) {
                            let content = currTranslation.substring(previousIndex);
                            let textSegment = document.createElement('span');
                            textSegment.innerText = content;
                            textSegment.style.cssText = style;
                            holder.appendChild(textSegment);
                        }
                        if (target.parentNode.parentNode.parentNode.childElementCount > 2){
                            let tagSegment = document.createElement('div');
                            tagSegment.style.fontFamily = "黑体";
                            tagSegment.style.color = "dodgerblue";
                            tagSegment.style.fontSize = "22px";

                            let spanLeft = document.createElement('span');
                            spanLeft.innerText = "由";
                            tagSegment.appendChild(spanLeft);

                            let tagImg = document.createElement('img');
                            tagImg.src = tagData;
                            tagImg.style.height = "25px";
                            tagSegment.appendChild(tagImg);

                            let spanRight = document.createElement('span');
                            spanRight.innerText = "翻译自日文：";
                            tagSegment.appendChild(spanRight);

                            target.appendChild(tagSegment);
                        }
                        target.appendChild(holder);
                    }
                }, dataURI, translation, style);

            } else {
                translation["0"] = await parseEmoji(req.body['translation']);
                await page.$eval('div[lang]', (element, tagData, translation, style) => {
                    let reg = /{\S+?}/g;
                    let currTranslation = translation["0"];
                    let match = reg.exec(currTranslation);
                    let previousIndex = 0;
                    let holder = document.createElement('div');
                    holder.lang = "zh";

                    while (match != null) {
                        if (match.index > previousIndex) {
                            let content = currTranslation.substring(previousIndex, match.index);
                            let textSegment = document.createElement('span');
                            textSegment.innerText = content;
                            textSegment.style.cssText = style;
                            holder.appendChild(textSegment);
                        }
                        let codePoint = match[0].substring(1, match[0].length - 1);
                        let imgSegment = document.createElement('span');
                        let emojiHolder = document.createElement('img');
                        emojiHolder.src = `https://abs-0.twimg.com/emoji/v2/svg/${codePoint}.svg`;
                        emojiHolder.style.height = "28px";
                        emojiHolder.style.width = "28px";
                        imgSegment.appendChild(emojiHolder);
                        holder.appendChild(imgSegment);

                        previousIndex = match.index + match[0].length;
                        match = reg.exec(currTranslation);
                    }
                    if (previousIndex !== currTranslation.length - 1) {
                        let content = currTranslation.substring(previousIndex);
                        let textSegment = document.createElement('span');
                        textSegment.innerText = content;
                        textSegment.style.cssText = style;
                        holder.appendChild(textSegment);
                    }
                    let tagSegment = document.createElement('div');
                    tagSegment.style.fontFamily = "黑体";
                    tagSegment.style.color = "dodgerblue";
                    tagSegment.style.fontSize = "22px";

                    let spanLeft = document.createElement('span');
                    spanLeft.innerText = "由";
                    tagSegment.appendChild(spanLeft);

                    let tagImg = document.createElement('img');
                    tagImg.src = tagData;
                    tagImg.style.height = "25px";
                    tagSegment.appendChild(tagImg);

                    let spanRight = document.createElement('span');
                    spanRight.innerText = "翻译自日文：";
                    tagSegment.appendChild(spanRight);

                    element.appendChild(tagSegment);
                    element.appendChild(holder);
                }, dataURI, translation, style)
            }

            console.log(maxIndex);
            let result = await takeScreenshot(page, maxIndex);
            await page.browser().close();
            res.send({
                status: true,
                screenshotPath: result.screenshotPath
            });
        }
    })()
})

app.listen(8000)