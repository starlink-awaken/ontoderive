"""
测试共享工具模块
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from utils import rf, wf, all_md, load_json, save_json


def test_rf_file_exists(z_park_path):
    text = rf(z_park_path / "facts" / "data.md")
    assert len(text) > 0
    assert "D-F1" in text


def test_rf_file_not_exists(tmp_path):
    text = rf(tmp_path / "nonexistent.md")
    assert text == ""


def test_wf_and_rf(tmp_path):
    path = tmp_path / "test.md"
    wf(path, "hello world")
    assert path.exists()
    assert rf(path) == "hello world"


def test_wf_creates_parent(tmp_path):
    path = tmp_path / "deep" / "nested" / "file.md"
    wf(path, "test")
    assert path.exists()


def test_all_md(z_park_path):
    files = all_md(z_park_path / "facts")
    assert len(files) >= 1
    assert all(f.suffix == ".md" for f in files)


def test_all_md_empty(tmp_path):
    files = all_md(tmp_path / "nonexistent")
    assert files == []


def test_load_json_success(tmp_path):
    import json
    path = tmp_path / "test.json"
    path.write_text(json.dumps({"key": "value"}))
    assert load_json(path) == {"key": "value"}


def test_load_json_fail(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json")
    assert load_json(path) is None


def test_load_json_not_exists(tmp_path):
    assert load_json(tmp_path / "nonexistent.json") is None


def test_save_json(tmp_path):
    path = tmp_path / "out.json"
    save_json(path, {"a": 1, "b": [2, 3]})
    assert path.exists()
    assert load_json(path) == {"a": 1, "b": [2, 3]}


def test_roundtrip(tmp_path):
    data = {"facts": 10, "entities": 5, "inferences": 3}
    path = tmp_path / "roundtrip.json"
    save_json(path, data)
    result = load_json(path)
    assert result == data
