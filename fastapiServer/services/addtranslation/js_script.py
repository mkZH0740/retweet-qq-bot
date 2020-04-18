import re


def add_emj_segment(segment_name:str,holder_name:str,src:str):
    cmd = f'var {segment_name} = document.createElement("img");'
    cmd += f'{segment_name}.src = "{src}";{segment_name}.style.width = "28px";{segment_name}.style.height = "28px";'
    cmd += f'{holder_name}.append({segment_name});'
    return cmd


def add_text_segment(segment_name:str,holder_name:str,text:str,style:str):
    cmd = f'var {segment_name} = document.createElement("span");'
    cmd += f'{segment_name}.lang = "zh";{segment_name}.style.cssText = "{style}";'
    cmd += f'{segment_name}.innerText = "{text}".replace(/&&/g,"\\n");'
    cmd += f'{holder_name}.append({segment_name});'
    return cmd


def add_text_holder(holder_name:str,target_name:str,i:int):
    cmd = f'var {target_name} = document.getElementsByTagName("article")[{i}].querySelector("div[lang]");'
    cmd += f'var {holder_name} = document.createElement("div");'
    cmd += f'{target_name}.append({holder_name});'
    return cmd


def process_comment_translation(text:str):
    pattern = re.compile('#[0-9][0-9]*')
    ops = list(pattern.findall(text))
    for i in range(len(ops)):
        ops[i] = int(ops[i].replace("#",''))
    texts = pattern.split(text)
    texts.pop(0)
    return {'ops':ops, 'texts':texts}


def process_single_line_text(text:str):
    res = list()
    pattern = re.compile('emj_[0-9][0-9]*')
    buf = pattern.search(text)
    while buf is not None:
        if buf.span()[0] != 0:
            res.append(text[:buf.span()[0]])
        res.append(buf.group())
        text = text[buf.span()[1]:]
        buf = pattern.search(text)
    if len(text) != 0:
        res.append(text)
    return res
