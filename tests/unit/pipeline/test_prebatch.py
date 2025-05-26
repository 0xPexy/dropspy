import json
from pipeline.prebatch import prebatch  # 경로는 프로젝트에 맞게 조정

def test_prebatch(tmp_path):
    # 1. 테스트 입력 데이터 준비 (중복/비중복 메시지 혼합)
    messages = [
        {"channel": "a", "time": "1", "text": "hello world"},
        {"channel": "b", "time": "2", "text": "hello world"},
        {"channel": "c", "time": "3", "text": "unique message"},
    ]
    input_file = tmp_path / "test_messages.json"
    output_dir = tmp_path

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(messages, f)

    # 2. prebatch 실행
    out_file = prebatch(str(input_file), str(output_dir))

    # 3. 결과 로딩 및 검증
    with open(out_file, "r", encoding="utf-8") as f:
        result = json.load(f)

    # 4. 유일 메시지만 남아야 하며, 각 메시지의 dup_count가 올바른지 체크
    assert len(result) == 2
    texts = {msg["text"]: msg for msg in result}
    assert texts["hello world"]["dup_count"] == 2
    assert texts["unique message"]["dup_count"] == 1
