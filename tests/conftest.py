"""
共享测试fixture
"""
import sys
from pathlib import Path
import pytest

# 保证engine模块可导入
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def project_root():
    """项目根路径"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def z_park_path(project_root):
    """z-park示例项目路径"""
    return project_root / "examples" / "z-park"


@pytest.fixture(scope="session")
def demo_quick_path(project_root):
    """demo-quick示例项目路径"""
    return project_root / "demo-quick"
