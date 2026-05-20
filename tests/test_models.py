"""
测试数据模型模块
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from engine.foundation.models import Fact, Entity, Inference, CheckResult, DeriveSnapshot


def test_fact_defaults():
    f = Fact(fid="D-F1", description="测试数据")
    assert f.fid == "D-F1"
    assert f.confidence == 0.95
    assert f.type == "data"
    assert f.source == ""
    assert f.value == ""


def test_fact_policy():
    f = Fact(fid="P-F9", description="政策A", type="policy", source="国务院")
    assert f.type == "policy"
    assert f.source == "国务院"


def test_entity():
    e = Entity(eid="ORG-测试", name="测试组织", entity_type="Organization", role="运营方", count="1")
    assert e.entity_type == "Organization"
    assert e.facts_ref == []


def test_entity_with_refs():
    e = Entity(eid="ROL-经理", name="经理人", entity_type="Role", facts_ref=["D-F1", "D-F2"])
    assert len(e.facts_ref) == 2
    assert "D-F1" in e.facts_ref


def test_inference():
    inf = Inference(iid="INF-L1", title="测试推论", derives_from=["D-F1", "D-F2"], confidence=0.85)
    assert inf.iid == "INF-L1"
    assert len(inf.derives_from) == 2
    assert inf.confidence == 0.85
    assert inf.tags == []


def test_check_result():
    cr = CheckResult(pid="C-01", name="事实基座完整性", passed=True, severity="PASS", detail="3个事实文件")
    assert cr.passed
    assert cr.severity == "PASS"
    assert cr.fixes == []
    assert cr.file == ""


def test_check_result_with_fixes():
    cr = CheckResult(pid="C-04", name="事实可追溯性", passed=False, severity="WARN",
                     detail="0/5事实被引用", fixes=["在推论中添加事实引用"])
    assert not cr.passed
    assert len(cr.fixes) == 1


def test_derive_snapshot():
    ds = DeriveSnapshot(timestamp="2026-05-18T10:00:00", facts=10, entities=5, inferences=3, scheme_files=1)
    assert ds.facts == 10
    assert ds.entities == 5
    assert ds.inferences == 3


def test_derive_snapshot_with_metrics():
    metrics = {"kqi": 0.42, "entropy": 5.6}
    ds = DeriveSnapshot(timestamp="2026-05-18T10:00:00", facts=8, entities=4, inferences=2, scheme_files=1, metrics=metrics)
    assert ds.metrics["kqi"] == 0.42
