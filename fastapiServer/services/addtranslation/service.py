from services.addtranslation.js_script import add_text_segment,add_text_holder,process_single_line_text,process_comment_translation,add_emj_segment
from fastapi import APIRouter
from splinter import Browser
from services.config import ROOTPATH
from pydantic import BaseModel
from PIL import Image
import os, json, traceback
router = APIRouter()


class AddTranslation(BaseModel):
    url:str
    tw_type:int
    group_id:str
    translation:str


@router.post('/add_translation')
async def add_translation(addtranslation:AddTranslation):
    browser = Browser('chrome', executable_path=f'{ROOTPATH}bin\\chromedriver.exe', headless=True)
    browser.visit(addtranslation.url)
    if not browser.is_element_present_by_tag('article', wait_time=8):
        return '?'
    if not os.path.exists(f'.\\configs\\{addtranslation.group_id}.json'):
        style = 'font-size: 25px;font-family: "黑体"'
    else:
        with open(f'.\\configs\\{addtranslation.group_id}.json', 'r', encoding='utf-8') as f:
            buf = json.load(f)
        style = buf['styles']
    try:
        if addtranslation.tw_type == 3:
            dynamics = browser.find_by_tag('article')
            cmd = ''
            buf = process_comment_translation(addtranslation.translation)
            for i in range(len(buf['texts'])):
                text = process_single_line_text(buf['texts'][i])
                print(text)
                emjs = dynamics[buf['ops'][i]-1].find_by_css('div[lang]').first.find_by_tag('img')
                cmd += add_text_holder(f'holder_{i + 1}', f'target_{i + 1}', buf['ops'][i] - 1)
                for part in text:
                    if part.find('emj') != -1:
                        cmd += add_emj_segment(f'emj_{i + 1}', f'holder_{i + 1}',
                                               emjs[int(part.replace('emj_', '')) - 1]['src'])
                    else:
                        cmd += add_text_segment(f'text_{i + 1}', f'holder_{i + 1}', part, style)
            print(cmd)
            browser.execute_script(cmd)
            last_index = buf['ops'][len(buf['ops']) - 1] - 1
            dynamics = browser.driver.find_elements_by_tag_name('article')
            start_location = dynamics[0].location
            stop_location = dynamics[last_index].location
            size = dynamics[last_index].size
            filepath = browser.screenshot(f'{ROOTPATH}cache\\', full=True)
            img = Image.open(filepath)
            img_processed = img.crop((start_location['x'], start_location['y'], stop_location['x'] + size['width'],
                                      stop_location['y'] + size['height']))
            os.remove(filepath)
            img_processed.save(filepath)
        else:
            dynamic = browser.find_by_tag('article').first
            emjs = dynamic.find_by_css('div[lang]').first.find_by_tag('img')
            text = process_single_line_text(addtranslation.translation)
            print(text)
            cmd = add_text_holder('holder_1', 'tar_1', 0)
            for i in range(len(text)):
                if text[i].find('emj') != -1:
                    cmd += add_emj_segment(f'emj_{i + 1}', f'holder_1',
                                           emjs[int(text[i].replace('emj_', '')) - 1]['src'])
                else:
                    cmd += add_text_segment(f'text_{i + 1}', f'holder_1', text[i], style)
            print(cmd)
            browser.execute_script(cmd)
            filepath = browser.find_by_tag('article').first.screenshot(f'{ROOTPATH}cache\\', full=True)
        return {'filepath': filepath}
    except Exception as e:
        traceback.print_exc()
        return '?'
    finally:
        browser.quit()
