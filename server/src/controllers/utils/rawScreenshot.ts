import { BoundingBox } from "puppeteer-core";
import { PageHolder } from "./preparePage";
import { TwitterMessage } from "src/component/Text";
import { tmpNameSync } from "tmp";


export async function rawTakeScreenshot(pageHolder: PageHolder, mainTweetIndex: number = -1, needContent: boolean = true){
    const page = pageHolder.page;

    let articles = await page.$$("article");
    let content = "";
    let boundingBox: BoundingBox;

    for (let i = 0; i < articles.length; i++) {
        const element = articles[i];
        const isMainTweet = await element.$eval("div[data-testid='tweet']", (tweetBoard) => {
            return tweetBoard.parentElement.childElementCount > 2;
        })

        if (i == 0)
            boundingBox = await element.boundingBox();
        else
            boundingBox.height += (await element.boundingBox()).height;
        
        if (needContent){
            let twitterMsg = new TwitterMessage(element);
            await twitterMsg.init();
            content += `第${i + 1}行： ${twitterMsg.toString()}`;
        }

        if ((mainTweetIndex == -1 && isMainTweet) || (i == mainTweetIndex)){
            break;
        }
    }

    let tempfileName = tmpNameSync({ postfix:".png", tmpdir: ".\\src\\cache"});
    try{
        await page.screenshot({ path: tempfileName, clip: boundingBox});
    }catch (err){
        return { status: false, msg: `@ rawScreenshot => ${err}`};
    }

    return { status: true, msg: tempfileName, content: content};
}