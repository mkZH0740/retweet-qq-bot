import { Controller, Get, Body } from '@nestjs/common';
import { ScreenshotService } from './screenshot.service';
import { launch, Browser } from 'puppeteer-core';
import { chromePath } from './utils/preparePage';

const browser: Promise<Browser> = launch({ product:"chrome", executablePath: chromePath });


@Controller("screenshot")
export class ScreenshotController{
    constructor(private readonly appService: ScreenshotService) {}

    @Get()
    public async screenshot(@Body("url") url: string){
        console.log(`${url} received!`);
        this.appService.browser = await browser;
        let result = await this.appService.takeScreenshot(url).catch((err) => {
            return {status:false, msg: `unknown ${err} @ controller`};
        });
        console.log(`returned ${result}`);
        return result;
    }
}