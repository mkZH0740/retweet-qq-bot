import { preparePage } from "./preparePage";
import { Page } from "puppeteer-core";
import { getContent, verifyPage, translateCodePoint } from './utils'
import { tmpNameSync } from 'tmp';


export async function takeScreenshot(url:string){
    const pageContent = await preparePage(url);
    let originalText:string;
    let result = {
        status: true,
        screenshot_path: "",
        original_text: "",
        error: ""
    }
    if (!pageContent.status){
        result.status = false; result.screenshot_path = null; result.error = pageContent.error;
    }else{
        const page: Page = pageContent.page;
        if (!await verifyPage(page)){
            await page.browser().close();
            result.status = false; result.screenshot_path = null; result.error = "@ takeScreenshot => nothing's on this page!";
            return result;
        }
        let pageData = await getContent(page, null);
        originalText = pageData.originalText;
        const screenshotPath = tmpNameSync({ postfix: '.png', tmpdir: './/src//cache' });
        try{
            await page.screenshot({ path: screenshotPath, clip: pageData.boundingBox });
            originalText = await translateCodePoint(originalText);
            result.status = true; result.screenshot_path = screenshotPath; result.original_text = originalText;
        }catch(error){
            result.status = false; result.screenshot_path = null; result.error = "@ takeScreenshot => unknown error!"
        }finally{
            await page.browser().close();
        }
        return result;
    }
}