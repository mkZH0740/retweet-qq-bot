import json
import os

from .settings import SETTING

default_group_setting = {
    "tweet": True,
    "retweet": True,
    "comment": True,
    "original_text": True,
    "translate": True,
    "content": True,
    "tag_path": f"{SETTING.group_tag_path}\\default_tag.png",
    "css_path": f"{SETTING.group_tag_path}\\default_text.css"
}


class GroupSetting:
    group_id: str
    group_setting: dict
    group_setting_path: str

    def __init__(self, group_id: str):
        self.group_id = group_id
        self.group_setting_path = f"{SETTING.group_setting_path}\\{self.group_id}.json"

        if os.path.exists(self.group_setting_path):
            self.group_setting = self._read_group_setting()
        else:
            self.group_setting = default_group_setting.copy()
            self._write_group_setting()

        if SETTING.debug:
            print(f"@ GroupSetting => LOAD {self.group_id} FINISHED")

    def update(self, change: dict):
        need_update = False
        for k, v in change.items():
            previous_setting = self.group_setting.get(k, None)
            if previous_setting is not None and v != previous_setting:
                previous_setting[k] = v
                need_update = True
        if need_update:
            self._write_group_setting()

    def _read_group_setting(self):
        with open(self.group_setting_path, "r", encoding="utf-8") as f:
            group_setting = json.load(f)
        return group_setting

    def _write_group_setting(self):
        with open(self.group_setting_path, "w", encoding="utf-8") as f:
            json.dump(self.group_setting, f, ensure_ascii=False, indent=4)


class GroupSettingHolder:
    group_settings: dict = {}

    def __init__(self):
        group_setting_filenames = os.listdir(SETTING.group_setting_path)
        for filename in group_setting_filenames:
            group_id = filename[: filename.rfind(".")]
            self.group_settings[group_id] = GroupSetting(group_id)
        if SETTING.debug:
            print("@ GroupSettingHolder => LOAD FINISHED")

    def update(self, group_id: str, change: dict):
        target_group_setting: GroupSetting = self.group_settings.get(
            group_id, None)
        if target_group_setting is None:
            print("none!")
            target_group_setting = GroupSetting(group_id)
        target_group_setting.update(change)
        self.group_settings[group_id] = target_group_setting

    def get(self, group_id: str) -> dict:
        target_group_setting: GroupSetting = self.group_settings.get(
            group_id, None)
        if target_group_setting is None:
            print("none!")
            target_group_setting = GroupSetting(group_id)
        if group_id not in self.group_settings:
            self.group_settings[group_id] = target_group_setting
        return target_group_setting.group_setting


group_setting_holder = GroupSettingHolder()
