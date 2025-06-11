import json
def jsonToStr(msg: dict) -> str:
    json_str = json.dumps(msg, ensure_ascii=False)
    return json_str

def print_filename_with_index(files: list[str]):
    for idx, filename in enumerate(files):
        print(f"{idx}: {filename}")