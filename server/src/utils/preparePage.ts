import { launch } from "puppeteer-core"

export async function preparePage(url:string){
    const browser = await launch({ product:"chrome", executablePath:"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"});
    const page = await browser.newPage();
    let retryTimes = 3;
    let needReload = true;
    while(retryTimes > 0 && needReload){
        try {
            let _ = await page.goto(url, { waitUntil: 'networkidle0', timeout: 8000 });
            needReload = false;
        } catch (error) {
            console.log("@ preparePage: timeout => " + error);
            retryTimes -= 1;
        }
    }
    if (needReload){
        return {
            "status": false,
            "page": null,
            "error": "@ preparePage: timeout"
        }
    }
    let maxViewPort = await page.evaluate(() => {
        return {
            height: Math.max(document.body.scrollHeight, document.body.offsetHeight),
            width: Math.max(document.body.scrollWidth, document.body.offsetWidth)
        }
    });
    await page.setViewport(maxViewPort); 
    return {
        "status": true,
        "page": page,
        "error": null
    }
}