"""E2E集成测试 — 全流程Pipeline+生态+MCP"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))


def test_e2e_derive_check_roundtrip():
    """完整推导+检查+报告闭环"""
    from derive import OntoDerive
    od = OntoDerive("examples/z-park")
    s = od.derive()
    assert s["facts"] >= 2
    assert "confidence_distribution" in s
    results = od.check()
    assert len(results) == 13
    report = od.generate_report()
    assert "事实数" in report


def test_e2e_pipeline_full():
    """Pipeline六阶段全流程"""
    from pipeline import DerivePipeline
    pipe = DerivePipeline("examples/z-park")
    pipe.set_goal("分析中关村", "科技园区")
    pipe.run()
    result = pipe.to_analysis_result()
    assert result.summary["facts"] >= 2


def test_e2e_toolforge_derive_link():
    """ToolForge匹配→指导→derive"""
    from toolforge.matcher import ToolForge
    from derive import OntoDerive
    tf = ToolForge()
    tools = tf.select("中关村科技园区分析")
    assert len(tools) >= 1
    guide = tf.to_inference_guide("中关村科技园区分析")
    assert "推荐" in guide
    od = OntoDerive("examples/z-park")
    s = od.derive()
    assert s["facts"] >= 2


def test_e2e_mcp_analyze():
    """MCP全量分析工具"""
    from mcp_server import handle_request
    resp = handle_request({
        "id": 99, "method": "tools/call",
        "params": {"name": "ontoderive_analyze",
                   "arguments": {"project": "examples/z-park", "goal": "中关村科技园区"}}
    })
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in result
    assert result["result"]["checks_total"] == 13


def test_e2e_typesystem_pipeline():
    """TypeValidator→check→C-07闭环"""
    from typesystem import TypeValidator
    from derive import OntoDerive
    tv = TypeValidator()
    r = tv.check_id("D-F1")
    assert r.is_valid
    od = OntoDerive("examples/z-park")
    results = od.check()
    c07 = [r for r in results if r["protocol_id"] == "C-07"]
    assert len(c07) == 1
    assert c07[0]["passed"]


def test_e2e_ecosystem_adapter_roundtrip():
    """Minerva→ecosystem→facts→derive闭环"""
    from ecosystem import minerva_to_facts
    from derive import OntoDerive
    import tempfile, os
    tmp = tempfile.mkdtemp()
    try:
        minerva_to_facts({"facts": [
            {"description": "测试数据", "value": "100", "source": "E2E测试"}
        ]}, tmp)
        od = OntoDerive(tmp)
        s = od.derive()
        assert s["facts"] >= 1
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
