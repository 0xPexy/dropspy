import json
def jsonToStr(msg: dict) -> str:
    json_str = json.dumps(msg, ensure_ascii=False)
    return json_str
