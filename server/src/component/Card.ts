import { ElementHandle } from "puppeteer-core";
import { Text, Emoji, TextComponent } from "./Text";


export class CardComponent{
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


export class VoteCard extends CardComponent{
    public content: (TextComponent[])[] = [];

    public async init(){
        let choices = await this.element.$$("div[dir='auto'] > span");
        for (let i = 0; i < choices.length; i++) {
            const currSpan = choices[i];
            let currChoice: TextComponent[] = [];
            let childSpans = await currSpan.$$("span");
            for (let j = 0; j < childSpans.length; j++) {
                const subSpan = childSpans[j];
                let isEmoji = (await subSpan.$("img")) != null;
                let temp: TextComponent;
                if (isEmoji){
                    temp = new Emoji(subSpan);
                }else{
                    temp = new Text(subSpan);
                }
                await temp.init();
                currChoice.push(temp);
            }
            this.content.push(currChoice);
        }
    }

    public toString(): string{
        return `[vote{${this.content.join(';')}}]`;
    }
}


export class Photo extends CardComponent{
    public url: string;

    // pass in div[testid='tweetPhoto']
    public async init(){
        this.url = await this.element.evaluate((element) => {
            let src = element.getAttribute("src");
            return src.substring(0, src.lastIndexOf("&"));
        }, this.element);
    }

    public toString(): string{
        return `url=${this.url}`;
    }
}


export class MultiPhoto extends CardComponent{
    public multiplePhotos: Photo[] = [];

    public async init(){
        let photos = await this.element.$$("img");
        for (let i = 0; i < photos.length; i++) {
            const currImg = photos[i];
            let currPhoto = new Photo(currImg);
            await currPhoto.init();
            this.multiplePhotos.push(currPhoto);
        }
    }

    public toString(): string{
        return `[img{${this.multiplePhotos.join(';')}}]`;
    }
}


export class TwitterCard{
    public element: ElementHandle;
    public component: CardComponent;
    
    constructor(element: ElementHandle){
        this.element = element;
    }
    
    public async init(){
        let cardBoard = (await this.element.evaluateHandle((element) => {
            let mainBoard = element.querySelector("div[lang]").parentElement.parentElement;
            if (mainBoard.childElementCount > 3){
                return mainBoard.childNodes[1];
            }else{
                return null;
            }
        }, this.element)).asElement();
        if (cardBoard != null){

            // only need vote and quote
            let isVote = (await cardBoard.$("div[data-testid='card.wrapper']")) != null;
            let isImage = (await cardBoard.$("div[data-testid='tweetPhoto']")) != null;

            if (isVote){
                this.component = new VoteCard(await this.element.$("div[data-testid='card.wrapper']"));
                await this.component.init();
            }else if (isImage){
                this.component = new MultiPhoto(cardBoard);
                await this.component.init();
            }
        }
    }

    public toString(): string{
        if (this.component == null){
            return "[]";
        }
        return this.component.toString();
    }
}