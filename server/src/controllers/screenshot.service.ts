import { Injectable } from '@nestjs/common'; 
import { Browser } from 'puppeteer-core';
import { PageHolder } from './utils/preparePage';
var AsyncLock = require('async-lock');

const lock = new AsyncLock;

@Injectable()
export class ScreenshotService{
    public browser: Browser;

    async takeScreenshot(url: string){
        let currPage = new PageHolder(this.browser, url);
        await currPage.preload();
        
        return lock.acquire("lock", () => {
            return (async ()=>{
                return await currPage.screenshot().catch((err) => {
                    currPage.free("takescreenshot err");
                    return {status: false, msg: err};
                })
            })();
        });
    }
}
