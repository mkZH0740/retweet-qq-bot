import json
import os

from typing import Dict

from .settings import SETTING


# hard coded group settings
default_group_setting = {
    "tweet": True,
    "retweet": True,
    "comment": True,
    "original_text": True,
    "translate": True,
    "content": True,
    "tag_path": f"{SETTING.group_tag_path}\\default_tag.png",
    "css_path": f"{SETTING.group_css_path}\\default_text.css"
}


class GroupSetting:
    """
    此类包装了群设置，用于缓存
    """
    group_id: str
    group_setting: dict
    group_setting_path: str

    def __init__(self, group_id: str):
        self.group_id = group_id
        self.group_setting_path = f"{SETTING.group_setting_path}\\{self.group_id}.json"

        if os.path.exists(self.group_setting_path):
            # 此群的群设置已经存在，直接读取设置
            self.group_setting = self._read_group_setting()
        else:
            # 此群的群设置尚未初始化，进行初始化生成本地文件
            self.group_setting = default_group_setting.copy()
            self._write_group_setting()

        if SETTING.debug:
            # 调试用
            print(f"@ GroupSetting => LOAD {self.group_id} FINISHED")

    def update(self, change: dict):
        """
        更新群设置
        :param change: 更新的设置键值对
        """
        # 判断是否需要更新本地文件
        need_update = False
        for k, v in change.items():
            # 获取原本群设置中键对应值，若键错误返回None
            previous_setting = self.group_setting.get(k, None)
            if previous_setting is not None and v != previous_setting:
                # 该键存在且与原来的值不同，更新对应值
                self.group_setting[k] = v
                need_update = True
        if need_update:
            # 写入新设置
            self._write_group_setting()

    def _read_group_setting(self) -> dict:
        """
        读取群设置
        :return: 群设置
        """
        with open(self.group_setting_path, "r", encoding="utf-8") as f:
            group_setting = json.load(f)
        return group_setting

    def _write_group_setting(self):
        """
        写入群设置
        """
        with open(self.group_setting_path, "w", encoding="utf-8") as f:
            json.dump(self.group_setting, f, ensure_ascii=False, indent=4)


class GroupSettingHolder:
    """
    此类保存了所有群设置
    """
    # 用字典保存群号对应的群设置
    group_settings: Dict[str, GroupSetting] = {}

    def __init__(self):
        # 读取群设置目录下所有设置文件
        group_setting_filenames = os.listdir(SETTING.group_setting_path)
        for filename in group_setting_filenames:
            group_id = filename[: filename.rfind(".")]
            self.group_settings[group_id] = GroupSetting(group_id)
        if SETTING.debug:
            print("@ GroupSettingHolder => LOAD FINISHED")

    def update(self, group_id: str, change: dict):
        """
        更新群号对应的群设置
        :param group_id: 群号
        :param change: 更新的群设置键值对
        """
        # 判断该群的群设置是否存在
        target_group_setting: GroupSetting = self.group_settings.get(
            group_id, None)
        if target_group_setting is None:
            # 不存在，初始化新群设置
            print("none!")
            target_group_setting = GroupSetting(group_id)
        # 更新设置
        target_group_setting.update(change)
        self.group_settings[group_id] = target_group_setting

    def get(self, group_id: str) -> dict:
        """
        获取群号对应的群设置
        :param group_id: 群号
        :return: 群号对应的群设置
        """
        target_group_setting: GroupSetting = self.group_settings.get(
            group_id, None)
        if target_group_setting is None:
            # 不存在，初始化新群设置
            print("none!")
            target_group_setting = GroupSetting(group_id)
        if group_id not in self.group_settings:
            # 该群设置尚未保存，保存群设置
            self.group_settings[group_id] = target_group_setting
        return target_group_setting.group_setting


# 全局群设置代理
group_setting_holder = GroupSettingHolder()
