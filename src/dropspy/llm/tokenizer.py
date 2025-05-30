from abc import ABC, abstractmethod

class Tokenizer(ABC):
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

class LocalTokenizer(Tokenizer):
    def count_tokens(self, text: str) -> int:
        return len(text.encode("utf-8")) // 2

class VertexTokenizer(Tokenizer):
    def __init__(self, model_name="gemini-1.5-flash-001"):
        from vertexai.preview import tokenization
        self.tokenizer = tokenization.get_tokenizer_for_model(model_name)
    def count_tokens(self, text: str) -> int:
        return self.tokenizer.count_tokens(text).total_tokens

class GeminiAPITokenizer(Tokenizer):
    def __init__(self, api_key: str, model_name="gemini-2.0-flash"):
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    def count_tokens(self, text: str) -> int:
        response = self.client.models.count_tokens(model=self.model_name, contents=text)
        return response.total_tokens
