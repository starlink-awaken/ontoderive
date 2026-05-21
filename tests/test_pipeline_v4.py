"""Tests for FormalPipeline — 四阶段形式化推理管线"""
from engine.reasoners.pipeline_v4 import FormalPipeline


def test_pipeline_creates():
    p = FormalPipeline()
    assert p is not None


def test_pipeline_run_empty():
    p = FormalPipeline()
    result = p.run("")
    assert isinstance(result, dict)
    assert "report" in result
