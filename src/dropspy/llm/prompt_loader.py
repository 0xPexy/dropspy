from pathlib import Path

class PromptLoader:
    def __init__(self, data_dir: str, encoding: str = "utf-8"):
        self.data_dir = Path(data_dir)
        self.encoding = encoding

    def load(self, prompt_name: str) -> str:
        prompt_path = self.data_dir / prompt_name
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        return prompt_path.read_text(encoding=self.encoding)
