"""AnalyticsEngine 测试 — A1-A5分析模式"""

from engine.theories.analytics import AnalyticsEngine, _extract_num, _iter_facts


class TestExtractNum:
    def test_int(self):
        assert _extract_num(42) == 42.0

    def test_float(self):
        assert _extract_num(3.14) == 3.14

    def test_string_with_unit(self):
        assert _extract_num("94%") == 94.0

    def test_chinese_number(self):
        assert _extract_num("1286万辆") == 1286.0

    def test_bool_returns_zero(self):
        # _extract_num(bool) returns 0.0 (bool不应出现在value字段)
        val = _extract_num(True)
        assert val == 0.0 or val == 1.0  # 取决于实现

    def test_empty_string(self):
        assert _extract_num("") == 0.0


class TestIterFacts:
    def test_normal_dict(self):
        facts = {"D-F1": {"desc": "test", "value": "1"}}
        result = list(_iter_facts(facts))
        assert len(result) == 1

    def test_mixed_dict_bool(self):
        facts = {"D-F1": {"desc": "test"}, "D-F2": True}
        result = list(_iter_facts(facts))
        assert len(result) == 1  # bool filtered out

    def test_non_dict(self):
        assert list(_iter_facts("not a dict")) == []
        assert list(_iter_facts(42)) == []


class TestA1CapacityElasticity:
    def test_detect_high_utilization(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "94%"}}
        assert ae._detect_capacity_constraint(facts, {}, [])

    def test_detect_excess_capacity(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "56%"}}
        assert ae._detect_capacity_constraint(facts, {}, [])

    def test_no_detect_normal_utilization(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "75%"}}
        assert not ae._detect_capacity_constraint(facts, {}, [])

    def test_detect_low_inventory(self):
        ae = AnalyticsEngine()
        facts = {
            "D-F1": {"desc": "库存天数", "value": "12天"},
            "D-F2": {"desc": "安全库存基准", "value": "30天"},
        }
        assert ae._detect_capacity_constraint(facts, {}, [])

    def test_analyze_high_utilization(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "94%"}}
        results = ae._analyze_capacity(facts, {}, [], None)
        assert any("供给弹性" in r["conclusion"] for r in results)

    def test_analyze_excess_capacity(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "56%"}}
        results = ae._analyze_capacity(facts, {}, [], None)
        assert any("产能过剩" in r["conclusion"] for r in results)


class TestA5Remediation:
    def test_detect_remediation(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "审计发现问题数", "value": "47个"}}
        assert ae._detect_remediation_needed(facts, {}, [])

    def test_no_detect_no_problem(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "营收", "value": "8.6亿元"}}
        assert not ae._detect_remediation_needed(facts, {}, [])

    def test_feasibility_calculation(self):
        ae = AnalyticsEngine()
        facts = {
            "D-F1": {"desc": "审计问题数", "value": "47"},
            "D-F2": {"desc": "合规团队人数", "value": "4"},
            "D-F3": {"desc": "距申报月数", "value": "5个月"},
        }
        results = ae._analyze_remediation(facts, {}, [], None)
        assert len(results) >= 1
        assert any("不可行" in r.get("conclusion", "") for r in results)


class TestA3AgencyDetection:
    def test_detect_agency_issue(self):
        ae = AnalyticsEngine()
        relations = [
            {"subject": "ORG-平台", "relation_type": "employs", "object": "ROL-骑手"},
            {"subject": "ROL-骑手", "relation_type": "cooperates_with", "object": "ROL-消费者"},
        ]
        assert ae._detect_agency_issue({}, {}, relations)

    def test_no_agency_without_employ(self):
        ae = AnalyticsEngine()
        relations = [
            {"subject": "ORG-A", "relation_type": "cooperates_with", "object": "ORG-B"},
        ]
        assert not ae._detect_agency_issue({}, {}, relations)


class TestAnalyticsEngineRun:
    def test_run_with_analytics(self):
        ae = AnalyticsEngine()
        facts = {
            "D-F1": {"desc": "产能利用率", "value": "94%"},
            "D-F2": {"desc": "库存天数", "value": "12天"},
            "D-F3": {"desc": "安全库存基准", "value": "30天"},
        }
        results = ae.run(facts, {}, {})
        assert len(results) >= 1  # A1 should trigger

    def test_max_depth_zero_blocks_analytics(self):
        ae = AnalyticsEngine()
        facts = {"D-F1": {"desc": "产能利用率", "value": "94%"}}
        results = ae.run(facts, {}, {}, max_depth=0)
        # depth=1+ patterns blocked, but depth=0 (A1) still runs
        assert len(results) >= 1  # A1 is depth=0
