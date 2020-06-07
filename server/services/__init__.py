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
    """
    :param data: 目标推特的URL和类型代码
    :return: 截图名和推特文字
    """
    res = await get_screenshot(data.url, data.tw_type)
    return res


@router.post("/add_translation")
async def translation(data: TranslationModel):
    """
    :param data: 目标推特的URL， 类型代码， 翻译文本和QQ群号
    :return: 截图路径
    """
    group_style_file = f"{ROOT_PATH}group_data\\{data.group_id}.json"
    if not os.path.exists(group_style_file):
        # 该群的样式库不存在，新建默认样式
        with open(group_style_file, "w", encoding="utf-8") as f:
            json.dump({"css-text": DEFAULT_STYLE}, f, ensure_ascii=False, indent=1)
        style = DEFAULT_STYLE
    else:
        # 该群的样式库存在，加载样式
        with open(group_style_file, "r", encoding="utf-8") as f:
            style = json.load(f)["css-text"]
    print(style)
    res = await add_translation(data.translation, style, data.url, data.tw_type)
    return res
