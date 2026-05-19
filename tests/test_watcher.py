"""文件监听器测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from watcher import FileWatcher


def test_watcher_init(tmp_path):
    (tmp_path / "facts").mkdir()
    (tmp_path / "scheme").mkdir()
    w = FileWatcher(str(tmp_path))
    assert w.root == tmp_path
    assert "facts" in w.watch_dirs


def test_watcher_check_no_changes(tmp_path):
    (tmp_path / "facts").mkdir()
    (tmp_path / "scheme").mkdir()
    w = FileWatcher(str(tmp_path))
    changes = w.check()
    assert changes == []


def test_watcher_detect_new_file(tmp_path):
    (tmp_path / "facts").mkdir()
    (tmp_path / "scheme").mkdir()
    # 先在snapshot前创建文件
    (tmp_path / "scheme" / "test.md").write_text("# Test")
    w = FileWatcher(str(tmp_path))
    # 再添加新文件
    (tmp_path / "facts" / "new_file.md").write_text("# New")
    changes = w.check()
    assert any(c[0] == "added" for c in changes)
