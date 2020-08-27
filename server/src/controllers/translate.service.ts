import { Injectable } from '@nestjs/common'; 
import { Browser } from 'puppeteer-core';
import { PageHolder } from './utils/preparePage';

var AsyncLock = require('async-lock');

const lock = new AsyncLock;

@Injectable()
export class TranslationService{
    public browser: Browser;

    async addTranslation(url: string, translation: string, cssPath: string, tagPath: string){
        let currPage = new PageHolder(this.browser, url);
        await currPage.preload();

        return lock.acquire("lock", () => {
            return (async ()=>{
                return await currPage.translation(translation, cssPath, tagPath).catch((err) => {
                    currPage.free("addtranslation err");
                    console.log(err);
                    return { status: false, msg: err};
                })
            })();
        });
    }
}