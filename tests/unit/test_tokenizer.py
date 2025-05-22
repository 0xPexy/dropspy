import pytest
import os
from llm.tokenizer import get_tokenizer
from config import GOOGLE_API_KEY

TEST_TEXTS = [
    "안녕하세요. This is a mixed sentence with English and 한글.",
    "🚀 에어드랍 참여 가이드:\n1. 채널 가입\n2. 폼 작성\n3. 인증 완료\n\n#에어드랍 #토큰",
    "긴 문단 테스트입니다. 마크다운 예시:\n```python\ndef hello():\n    print('hi')\n```\n여기까지.",
    "1. Visit https://dropspy.com\n2. Follow @DropSpy\n3. Claim now!\n\n🔥 Hurry up!",
]


@pytest.mark.parametrize("text", TEST_TEXTS)
def test_tokenizers(text):
    local = get_tokenizer("local")
    print(f"LocalTokenizer: {local.count_tokens(text)} tokens")
    try:
        vertex = get_tokenizer("vertex", model_name="gemini-1.5-flash-001")
        print(f"VertexTokenizer: {vertex.count_tokens(text)} tokens")
    except Exception as e:
        print(f"VertexTokenizer error: {e}")
    try:
        api_key = GOOGLE_API_KEY
        if api_key:
            gemini = get_tokenizer("gemini", api_key=api_key)
            print(f"GeminiAPITokenizer: {gemini.count_tokens(text)} tokens")
    except Exception as e:
        print(f"GeminiAPITokenizer error: {e}")
