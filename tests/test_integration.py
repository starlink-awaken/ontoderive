"""生态集成测试 — Minerva→OntoDerive→Sophia→Agora全链路"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))


def test_minerva_to_ontoderive_full_flow(tmp_path):
    """Minerva研究→OntoDerive事实→derive→check完整闭环"""
    from ecosystem import minerva_to_facts
    from derive import OntoDerive

    research = {
        "facts": [
            {"description": "企业数", "value": "240", "source": "Minerva研究2026"},
            {"description": "对接量", "value": "80次/年", "source": "运营报告"},
            {"description": "转化率", "value": "8%", "source": "行业统计"},
        ],
        "policies": [{"name": "科技成果转化法", "authority": "全国人大", "date": "2025"}],
    }
    minerva_to_facts(research, str(tmp_path))
    (tmp_path / "inferences").mkdir(exist_ok=True)
    (tmp_path / "inferences" / "analysis.md").write_text(
        "## INF-L1：供需矛盾\n推导：D-F1=240企业但D-F3=8%转化率，需要平台\n- derives_from: [D-F1, D-F3]\n"
    )
    (tmp_path / "scheme").mkdir(exist_ok=True)
    (tmp_path / "scheme" / "report.md").write_text("# 平台方案\n基于D-F1分析")
    (tmp_path / "_derivation_logs").mkdir(exist_ok=True)
    od = OntoDerive(str(tmp_path))
    s = od.derive()
    assert s["facts"] >= 3
    results = od.check()
    assert len(results) == 13
    passed = sum(1 for r in results if r["passed"])
    assert passed >= 8


def test_toolforge_sophia_link():
    """ToolForge→Sophia范式推荐→推导指导"""
    from toolforge.matcher import ToolForge
    from ecosystem import recommend_frameworks

    tools = recommend_frameworks("高校科研评价体系改革")
    assert isinstance(tools, list)
    assert len(tools) >= 1
    guide = ToolForge().to_inference_guide("高校科研评价体系改革")
    assert "推荐推导框架" in guide


def test_agora_mcp_routing():
    """Agora路由→MCP工具→OntoDerive"""
    from ecosystem import AgoraAdapter
    assert AgoraAdapter.can_handle("ontoderive_derive")
    assert AgoraAdapter.can_handle("toolforge_select")
    assert not AgoraAdapter.can_handle("unknown_tool")


def test_ecos_pipeline_observer():
    """eCOS Observer→Pipeline事件订阅"""
    from ecosystem import create_observer
    obs = create_observer()
    obs.on_stage_start("derive", {"project_root": "/tmp/test"})
    obs.on_stage_end("derive", {"facts": 10})
    obs.on_error("check", Exception("test error"))
    events = obs.get_events()
    assert len(events) == 3
    assert events[0]["@type"] == "PipelineStageStarted"
    assert events[2]["@type"] == "PipelineError"


def test_multi_hop_derivation():
    """多层推导链：D-F→INF-L1→INF-L2"""
    from bayesian import BayesianNetwork
    bn = BayesianNetwork()
    bn.add_fact("D-F1", 0.95, "事实1")
    bn.add_fact("D-F2", 0.90, "事实2")
    bn.add_inference("INF-L1：供需矛盾", ["D-F1", "D-F2"], 0.85, "推论1")
    bn.add_inference("INF-L2：平台方案", ["INF-L1：供需矛盾"], 0.80, "推论2")
    bn.finalize()
    assert len(bn.detect_cycles()) == 0
    result = bn.propagate()
    conf_l1 = result["nodes"].get("INF-L1：供需矛盾", {}).get("confidence", 0)
    conf_l2 = result["nodes"].get("INF-L2：平台方案", {}).get("confidence", 0)
    assert conf_l1 > 0.8, f"L1 conf={conf_l1}"
    assert conf_l2 > 0.65, f"L2 conf={conf_l2}"
    assert conf_l2 < conf_l1, f"间接推导置信度应低于直接推导"
