"""Tests for InsightEngine"""
from engine.intelligence.insight import Insight, InsightEngine


class TestInsight:
    def test_defaults(self):
        ins = Insight(type="derivation", content="测试洞察", confidence=0.85)
        assert ins.type == "derivation"
        assert ins.content == "测试洞察"
        assert ins.confidence == 0.85
        assert ins.method == "llm"

    def test_with_model(self):
        ins = Insight(type="quality", content="质量洞察", confidence=0.9, method="llm", model="test-model")
        assert ins.type == "quality"
        assert ins.model == "test-model"


class TestInsightEngine:
    def test_create(self):
        engine = InsightEngine()
        assert engine is not None

    def test_derive_insights_no_enhancer(self, tmp_project):
        engine = InsightEngine(enhancer=None)
        insights = engine.derive_insights(
            project_root=tmp_project,
            facts_summary="测试事实",
            inferences_text="测试推论",
        )
        assert insights == []
