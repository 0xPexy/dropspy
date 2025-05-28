import pytest
from llm.tokenizer import LocalTokenizer, VertexTokenizer

TEST_TEXTS = [
    "안녕하세요. This is a mixed sentence with English and 한글.",
    "🚀 에어드랍 참여 가이드:\n1. 채널 가입\n2. 폼 작성\n3. 인증 완료\n\n#에어드랍 #토큰",
    "긴 문단 테스트입니다. 마크다운 예시:\n```python\ndef hello():\n    print('hi')\n```\n여기까지.",
    "1. Visit https://dropspy.com\n2. Follow @DropSpy\n3. Claim now!\n\n🔥 Hurry up!",
]

expected_local_tokens = [33, 53, 54, 38]
expected_vertex_tokens = [15, 39, 34, 27]


@pytest.mark.parametrize(
    "text, expected_local, expected_vertex",
    zip(TEST_TEXTS, expected_local_tokens, expected_vertex_tokens),
)
def test_tokenizers(text, expected_local, expected_vertex):
    local = LocalTokenizer()
    local_tokens = local.count_tokens(text)
    assert local_tokens == expected_local
    try:
        vertex = VertexTokenizer(model_name="gemini-1.5-flash-001")
        vertex_tokens = vertex.count_tokens(text)
        assert vertex_tokens == expected_vertex
    except AssertionError as e:
        raise AssertionError(f"VertexTokenizer tokens mismatch: {e}")
    except Exception as e:
        print(f"VertexTokenizer error: {e}")
