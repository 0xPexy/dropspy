import pytest
import json
from pathlib import Path
from dropspy.utils.json_store import JSONStore


@pytest.fixture
def file_store(tmp_path):
    return JSONStore(tmp_path)


def test_list_files(file_store):
    file1 = file_store.data_dir / "file1.json"
    file2 = file_store.data_dir / "file2.txt"
    file3 = file_store.data_dir / "file3.json"
    file1.touch()
    file2.touch()
    file3.touch()

    assert file_store.list_files() == [file1.name, file3.name]


def test_print_file_list(capsys, file_store):
    file1 = file_store.data_dir / "file1.json"
    file2 = file_store.data_dir / "file3.json"
    file1.touch()
    file2.touch()

    file_store.print_file_list()

    captured = capsys.readouterr()
    assert captured.out == "0: file1.json\n1: file3.json\n"


def test_get_file_by_index(file_store):
    file1 = file_store.data_dir / "file1.json"
    file2 = file_store.data_dir / "file3.json"
    file1.touch()
    file2.touch()
    file_store.get_file_by_index(0)
    assert file_store.get_file_by_index(0)["filename"] == file1.name
    assert file_store.get_file_by_index(1)["filename"] == file2.name

    with pytest.raises(IndexError):
        file_store.get_file_by_index(2)


def test_save_and_load(file_store):
    data = {"key": "value"}
    filename = "test.json"
    file_store._save(filename, data)

    assert (file_store.data_dir / filename).exists()

    loaded_data = file_store._load(filename)
    assert loaded_data == data

def test_save_load_list(file_store):
    data = [{"key1": "value1"}, {"key2": "value2"}]
    filename = "test.json"
    file_store._save(filename, data)

    assert (file_store.data_dir / filename).exists()

    loaded_data = file_store._load(filename)
    assert loaded_data == data