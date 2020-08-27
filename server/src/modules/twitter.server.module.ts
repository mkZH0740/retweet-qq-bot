import { Module } from "@nestjs/common";
import { ScreenshotController } from "src/controllers/screenshot.controller";
import { ScreenshotService } from "src/controllers/screenshot.service";
import { TranslationController } from "src/controllers/translate.controller";
import { TranslationService } from "src/controllers/translate.service";


@Module({
    controllers: [ScreenshotController, TranslationController],
    providers: [ScreenshotService, TranslationService]
})
export class TwitterServerModule {}