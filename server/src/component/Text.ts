import { ElementHandle } from "puppeteer-core";
import { convert } from "twemoji";


export class TextComponent{
    public element: ElementHandle;

    constructor(element: ElementHandle){
        this.element = element;
    }

    public async init(){

    }

    public toString(): string{
        return "";
    }
}


export class Text extends TextComponent{
    public lang: string;
    public text: string;

    public async init(){
        this.lang = await this.element.evaluate((element) => {
            return element.parentElement.lang;
        }, this.element);
        this.text = await this.element.evaluate((element) => {
            return element.innerHTML.replace(/\n/g, "\\n");
        }, this.element);
    }

    public toString(): string{
        return `${this.text}`;
    }
}


export class Emoji extends TextComponent{
    public emojiCode: string;
    public emojiUrl: string;
    public emoji: string;

    public async init(){
        this.emojiUrl = await this.element.evaluate((element) => {
            return element.querySelector("img").src;
        });
        this.emojiCode = this.emojiUrl.substring(this.emojiUrl.lastIndexOf("/") + 1, this.emojiUrl.lastIndexOf("."));
        this.emoji = convert.fromCodePoint(this.emojiCode);
    }

    public toString(): string{
        return `${this.emoji}`;
    }
}


export class Link extends TextComponent{
    public url: string;

    public async init(){
        this.url = await this.element.evaluate((element) => {
            return element.parentElement.title;
        }, this.element)
    }

    public toString(): string{
        return `${this.url}`;
    }
}

export class HashTag extends TextComponent{
    public atName: string;

    public async init(){
        this.atName = await this.element.evaluate((element) => {
            return element.querySelector("a").innerText;
        }, this.element)
    }

    public toString(): string{
        return `@${this.atName}`;
    }
}


export class TwitterMessage{
    public content: (TextComponent)[] = [];
    public element: ElementHandle;

    // pass in article
    constructor(element: ElementHandle){
        this.element = element;
    }

    public async init(){
        let messageBoard = await this.element.$("div[lang]")

        let childSpans = await messageBoard.$$("span");
        for (let i = 0; i < childSpans.length; i++) {
            const currElement = childSpans[i];
            let temp: TextComponent;

            let isEmoji = (await currElement.$("img")) != null;
            let isLink = await currElement.evaluate((element) => {
                console.log(element);
                return element.getAttribute("aria-hidden") == "true";
            }, currElement);
            let isHashTag = (await currElement.$("a")) != null;

            if (isEmoji){
                temp = new Emoji(currElement);
            }else if (isLink){
                temp = new Link(currElement);
            }else if (isHashTag){
                temp = new HashTag(currElement);
            }else{
                temp = new Text(currElement);
            }
            await temp.init();
            this.content.push(temp);
        }
    }

    public toString(): string{
        let result = "";
        for (let i = 0; i < this.content.length; i++)
            result += this.content[i].toString();
        return result;
    }
}