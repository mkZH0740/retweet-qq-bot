import os

from .settings import SETTING


def add_group_log(group_id: str, url: str) -> int:
    log_path = f"{SETTING.group_log_path}\\{group_id}.txt"
    if not os.path.exists(log_path):
        open(log_path, "w", encoding="utf-8")
    with open(log_path, "r+", encoding="utf-8") as f:
        previous_content = f.readlines()
    previous_content.append(url)
    index = len(previous_content)
    if index > 5000:
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(previous_content[5000:])
            index -= 5000
    else:
        with open(log_path, "a+", encoding="utf-8") as f:
            f.write(previous_content.pop())
    return index

# input real index


def read_group_log(group_id: str, index: int) -> str:
    log_path = f"{SETTING.group_log_path}\\{group_id}.txt"
    with open(log_path, "r", encoding="utf-8") as f:
        previous_content = f.readlines()
    if index < 0 or index > len(previous_content) - 1:
        raise RuntimeError("嵌字编号不合法！")
    return previous_content[index].strip()
