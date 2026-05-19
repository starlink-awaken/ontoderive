"""
测试 derive 引擎核心流程
"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from derive import OntoDerive


def test_init_project(tmp_path):
    od = OntoDerive(tmp_path)
    assert od.facts_dir == tmp_path / "facts"
    assert od.entities_dir == tmp_path / "entities"
    assert od.inferences_dir == tmp_path / "inferences"
    assert od.scheme_dir == tmp_path / "scheme"
    assert od.log_dir == tmp_path / "_derivation_logs"
    assert od.log_dir.exists()


def test_derive(z_park_path):
    od = OntoDerive(z_park_path)
    summary = od.derive()
    assert summary["facts"] >= 2
    assert summary["scheme_files"] >= 1
    assert "derived_at" in summary


def test_check(z_park_path):
    od = OntoDerive(z_park_path)
    results = od.check()
    assert len(results) == 13  # C-01 ~ C-13
    passed = sum(1 for r in results if r["passed"])
    assert passed >= 8  # z-park应该大部分通过
    # 验证结果文件格式
    for r in results:
        assert "protocol_id" in r
        assert "passed" in r
        assert "severity" in r
        assert "detail" in r


def test_generate_report(z_park_path):
    od = OntoDerive(z_park_path)
    od.derive()
    od.check()
    report = od.generate_report()
    assert "事实数" in report
    report_path = od.log_dir / "report.md"
    assert report_path.exists()


def test_resolve_new_project(tmp_path):
    od = OntoDerive(tmp_path)
    # 创建一个空check结果并测试resolve
    od.log_dir.mkdir(parents=True, exist_ok=True)
    (od.log_dir / "check-result.json").write_text(json.dumps({
        "details": [
            {"protocol_id": "C-01", "passed": False, "fixes": ["创建 facts/data.md 和 facts/policy.md"]}
        ]
    }))
    fixed = od.resolve()
    assert fixed >= 1
    assert (tmp_path / "facts").exists()


def test_run_rounds(z_park_path):
    od = OntoDerive(z_park_path)
    od.run_rounds(rounds=2)
    # 2轮后应有derive-summary和check-result
    assert (od.log_dir / "derive-summary.json").exists()
    assert (od.log_dir / "check-result.json").exists()


def test_empty_project_derive(tmp_path):
    od = OntoDerive(tmp_path)
    summary = od.derive()
    assert summary["facts"] == 0
    assert summary["inferences"] == 0


def test_empty_project_check(tmp_path):
    od = OntoDerive(tmp_path)
    results = od.check()
    assert len(results) == 13
    # 空项目C-01应该是BLOCKER
    c01 = [r for r in results if r["protocol_id"] == "C-01"]
    assert len(c01) == 1
    assert not c01[0]["passed"]
    assert c01[0]["severity"] == "BLOCKER"
