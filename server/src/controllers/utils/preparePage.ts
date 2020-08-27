import { Page, Browser } from "puppeteer-core";
import { rawTakeScreenshot } from "./rawScreenshot";
import { addTranslation } from "./addTranslation";
import { readFileSync } from "fs";

export const chromePath = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe";

export class PageHolder{
    public browser: Browser;
    public page: Page;

    public url: string;


    public constructor(browser: Browser, url: string){
        this.browser = browser;
        this.url = url;
    }

    public async free(from: string){
        if (!this.page.isClosed())
            await this.page.close();
        console.log(`${this.url} freed! @ ${from}`);
    }

    public async preload(){
        this.page = await this.browser.newPage();
        await this.page.goto(this.url, { waitUntil: 'networkidle0', timeout: 8000 }).catch((err) => {
            console.log(err);
        });
    }

    public async verify(){
        let target = await this.page.$("article");
        if (target == null)
            return false;
        return true;
    }

    public async retry(times: number = 0){
        let verified = await this.verify();
        while (!verified && times < 3){
            await this.page.reload({ waitUntil: 'networkidle0', timeout: 8000 }).catch((err) => console.log(err));
            verified = await this.verify();
            times ++;
        }
        if (!verified || times == 3){
            throw "load failed!"
        }
    }

    public async setMaxViewPort(){
        let maxViewPort = await this.page.evaluate(() => {
            return {
                height: Math.max(document.body.scrollHeight, document.body.offsetHeight),
                width: Math.max(document.body.scrollWidth, document.body.offsetWidth)
            }
        });
        await this.page.setViewport(maxViewPort);
    }
    
    public async beforeRun(){
        await this.retry();
        await this.setMaxViewPort();
    }

    public async screenshot(){
        await this.page.bringToFront();
        await this.beforeRun();
        let result = await rawTakeScreenshot(this).then((value) => {
            this.free("preparePage.screenshot")
            return value;
        });
        console.log(`ready to return ${result}`);
        return result;
    }

    public async translation(translation: string, cssPath: string, tagPath: string){
        await this.page.bringToFront();
        await this.beforeRun();
        let cssStyle = readFileSync(cssPath, { encoding: "utf-8" });
        let tagData = 'data:image/png;base64,' + readFileSync(tagPath, { encoding: "base64" });
        let maxIndex = await addTranslation(this, translation, cssStyle, tagData);

        await this.setMaxViewPort();

        let result = await rawTakeScreenshot(this, maxIndex, false).then((value) => {
            this.free("preparePage.translation")
            return value;
        });

        console.log(`ready to return ${result}`);
        return result;
    }
}