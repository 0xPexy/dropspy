import pytest
from dropspy.llm.prompt_loader import PromptLoader


def test_prompt_loader_load_success(tmp_path):
    data_dir = tmp_path
    prompt_file = "first_filter.md"
    text = "prompt example\nexample prompt\nprompt example\n"
    (data_dir / prompt_file).write_text(text, encoding="utf-8")

    loader = PromptLoader(str(data_dir))
    assert loader.load(prompt_file) == text


def test_prompt_loader_file_not_found(tmp_path):
    loader = PromptLoader(str(tmp_path))
    with pytest.raises(FileNotFoundError):
        loader.load("not_exist.md")
