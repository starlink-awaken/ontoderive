"""生态适配器测试"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from ecosystem import minerva_to_facts, recommend_frameworks, AgoraAdapter, create_observer


def test_minerva_to_facts(tmp_path):
    research = {"facts": [{"description": "测试数据", "value": "100", "source": "测试"}]}
    r = minerva_to_facts(research, str(tmp_path))
    assert r["facts_files"] == 1
    assert (tmp_path / "facts" / "data.md").exists()


def test_minerva_with_policies(tmp_path):
    research = {
        "facts": [{"description": "数据1", "value": "50", "source": "src"}],
        "policies": [{"name": "政策A", "authority": "国务院", "date": "2026"}],
    }
    r = minerva_to_facts(research, str(tmp_path))
    assert r["policy_files"] == 1


def test_recommend_frameworks():
    recs = recommend_frameworks("分析市场")
    assert isinstance(recs, list)


def test_agora_can_handle():
    assert AgoraAdapter.can_handle("ontoderive_derive")
    assert AgoraAdapter.can_handle("toolforge_select")
    assert not AgoraAdapter.can_handle("unknown_tool")


def test_agora_route_derive():
    r = AgoraAdapter.route("ontoderive_derive", {}, "examples/z-park")
    assert "facts" in r


def test_agora_route_toolforge():
    r = AgoraAdapter.route("toolforge_select", {"goal": "分析市场"}, ".")
    assert "tools" in r


def test_ecos_observer():
    obs = create_observer()
    obs.on_stage_start("derive", {"project_root": "/tmp/test"})
    obs.on_stage_end("derive", {"summary": "ok"})
    events = obs.get_events()
    assert len(events) == 2
    assert events[0]["@type"] == "PipelineStageStarted"
    assert events[1]["@type"] == "PipelineStageCompleted"
