import os
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

# 测试环境禁用LLM，避免ollama冷启动导致测试超时
os.environ.setdefault("ONTODERIVE_LLM_BACKEND", "none")

@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def z_park_path(project_root):
    return project_root / "examples" / "z-park"
