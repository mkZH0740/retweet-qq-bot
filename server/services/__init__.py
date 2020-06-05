import json
import os

from fastapi import APIRouter
from pydantic import BaseModel

from .configs import ROOT_PATH, DEFAULT_STYLE
from .screenshot import get_screenshot
from .translation import add_translation

router = APIRouter()


class ScreenshotModel(BaseModel):
    url: str
    tw_type: int


class TranslationModel(BaseModel):
    url: str
    tw_type: int
    translation: str
    group_id: str


@router.post("/get_screenshot")
async def screenshot(data: ScreenshotModel):
    res = await get_screenshot(data.url, data.tw_type)
    return res


@router.post("/add_translation")
async def translation(data: TranslationModel):
    group_style_file = f"{ROOT_PATH}group_data\\{data.group_id}.json"
    if not os.path.exists(group_style_file):
        with open(group_style_file, "w", encoding="utf-8") as f:
            json.dump({"css-text": DEFAULT_STYLE}, f, ensure_ascii=False, indent=1)
        style = DEFAULT_STYLE
    else:
        with open(group_style_file, "r", encoding="utf-8") as f:
            style = json.load(f)["css-text"]
    print(style)
    res = await add_translation(data.translation, style, data.url, data.tw_type)
    return res
