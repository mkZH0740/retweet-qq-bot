import os

from .settings import SETTING


def add_group_log(group_id: str, url: str) -> int:
    """
    加入群日志
    :param group_id: 群号
    :param url: 推文链接
    :return: 行数，即嵌字编号
    """
    log_path = f"{SETTING.group_log_path}\\{group_id}.txt"
    if not os.path.exists(log_path):
        # 群日志文件不存在，新建日志文件
        open(log_path, "w", encoding="utf-8")
    with open(log_path, "r+", encoding="utf-8") as f:
        # 读取原有日志
        previous_content = f.readlines()
    # 加入新纪录
    previous_content.append(f"{url}\n")
    index = len(previous_content)
    if index > 5000:
        # 长于5000行，删除前5000行重新开始记录
        with open(log_path, "w", encoding="utf-8") as f:
            f.writelines(previous_content[5000:])
            index -= 5000
    else:
        with open(log_path, "a+", encoding="utf-8") as f:
            f.write(previous_content.pop())
    return index


def read_group_log(group_id: str, index: int) -> str:
    """
    读取群日志
    :param group_id: 群号
    :param index: 日志记录的真实序号（-1）
    :return: 记录的推文链接
    """
    log_path = f"{SETTING.group_log_path}\\{group_id}.txt"
    with open(log_path, "r", encoding="utf-8") as f:
        previous_content = f.readlines()
    if index < 0 or index > len(previous_content) - 1:
        raise RuntimeError("嵌字编号不合法！")
    return previous_content[index].strip()
