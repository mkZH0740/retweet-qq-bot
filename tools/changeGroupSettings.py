import json, os

osList = os.listdir(".//groups")

for file in osList:
    if file.find(".json") != -1:
        with open(f".//groups//{file}", "r", encoding="utf-8") as f:
            prev = json.load(f)
        tag: str = prev["tag"]
        tag = tag.replace("mike", "Administrator")
        prev["tag"] = tag
        with open(f".//groups//{file}", "w", encoding="utf-8") as f:
            json.dump(prev, f, ensure_ascii=False, indent=1)
        print(f"SOLVED => {file}")