from typing import Protocol

class Tokenizer(Protocol):
    def count_tokens(self, text: str) -> int:
        ...

class LocalTokenizer:
    def count_tokens(self, text: str) -> int:
        return len(text.encode("utf-8")) // 2

class VertexTokenizer:
    def __init__(self, model_name="gemini-1.5-flash-001"):
        from vertexai.preview import tokenization
        self.tokenizer = tokenization.get_tokenizer_for_model(model_name)
    def count_tokens(self, text: str) -> int:
        return self.tokenizer.count_tokens(text).total_tokens

class GeminiAPITokenizer:
    def __init__(self, api_key: str, model_name="gemini-2.0-flash"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    def count_tokens(self, text: str) -> int:
        response = self.client.models.count_tokens(model=self.model_name, contents=text)
        return response.total_tokens

def get_tokenizer(kind: str, **kwargs) -> Tokenizer:
    if kind == "local":
        return LocalTokenizer()
    elif kind == "vertex":
        return VertexTokenizer(kwargs.get("model_name", "gemini-1.5-flash-001"))
    elif kind == "gemini":
        return GeminiAPITokenizer(
            kwargs["api_key"],
            kwargs.get("model_name", "gemini-2.0-flash"),
        )
    else:
        raise ValueError(f"Unknown tokenizer kind: {kind}")
