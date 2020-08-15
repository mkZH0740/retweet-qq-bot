import { Controller, Get, Post, Body } from '@nestjs/common';
import { AppService } from './app.service';
import { takeScreenshot } from './utils/takeScreenshot';
import { addTranslation } from './utils/addTranslation';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) { }

  @Post("/screenshot")
  async takeScreenshot(@Body("url")url:string) {
    const result = await takeScreenshot(url);
    console.log(result);
    return result;
  }

  @Post("/translate")
  async translate(@Body("url")url:string, @Body("translation") translation:string, @Body("tagPath")tagPath:string, @Body("cssPath")cssPath:string){
    const result = await addTranslation(url, translation, tagPath, cssPath);
    console.log(result);
    return result;
  }

  @Get()
  getHello(): string {
    return this.appService.getHello();
  }
}
