"""LLM增强层测试 — 降级方案验证"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from engine.intelligence.llm import LLMEnhancer, get_enhancer


def test_enhancer_init():
    e = LLMEnhancer(backend="none")
    assert e.backend == "none"
    assert not e.available


def test_enhancer_none_backend():
    e = LLMEnhancer(backend="none")
    # 降级：无LLM时返回原提示
    hints = e.enhance_derivation_hints("测试", "推论内容", ["提示1"])
    assert hints == ["提示1"]


def test_enhancer_no_contradiction_without_llm():
    e = LLMEnhancer(backend="none")
    r = e.detect_contradictions("推论A", "推论B", ["D-F1"])
    assert r is None


def test_smart_match_without_llm():
    e = LLMEnhancer(backend="none")
    tools = [{"id": "M-001", "name": "SWOT", "description": "分析框架"}]
    r = e.smart_match_tools("分析市场", "", tools)
    assert r is None


def test_get_enhancer_cached():
    e1 = get_enhancer()
    e2 = get_enhancer()
    assert e1 is e2  # 单例缓存


def test_get_enhancer_force():
    e1 = get_enhancer()
    e2 = get_enhancer(force=True)
    assert e1 is not e2  # 强制刷新
