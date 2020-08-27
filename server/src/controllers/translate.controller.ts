import { launch, Browser } from 'puppeteer-core';
import { chromePath } from './utils/preparePage';
import { Controller, Post, Body } from '@nestjs/common';
import { TranslationService } from './translate.service';

const browser: Promise<Browser> = launch({ product: "chrome", executablePath: chromePath });


@Controller("translation")
export class TranslationController {
    constructor(private readonly appService: TranslationService) { }

    @Post()
    public async translate(@Body("url") url: string, 
                            @Body("translation") translation: string, 
                            @Body("css-path") cssPath: string, 
                            @Body("tag-path") tagPath: string) 
    {
        console.log(`${url} received!`);
        this.appService.browser = await browser;
        let result = await this.appService.addTranslation(url, translation, cssPath, tagPath).catch((err) => {
            return { status: false, msg: `unknown ${err} @ controller`};
        });
        console.log(`returned ${result}`);
        return result;
    }
}