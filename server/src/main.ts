import { NestFactory } from '@nestjs/core';
import { TwitterServerModule } from './modules/twitter.server.module';

async function bootstrap() {
  const app = await NestFactory.create(TwitterServerModule);
  await app.listen(3000);
}
bootstrap();
