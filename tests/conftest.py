import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

@pytest.fixture(scope="session")
def project_root():
    return Path(__file__).parent.parent

@pytest.fixture(scope="session")
def z_park_path(project_root):
    return project_root / "examples" / "z-park"
