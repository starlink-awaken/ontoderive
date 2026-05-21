# OntoDerive 架构治理计划 (v2 — 2026-05-21 更新)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 全面治理架构审计发现的P0-P3问题，包括打包修复、死模块清理、测试覆盖补齐、代码质量重构、分层违规整改

**架构:** 按依赖顺序分4个阶段推进。Phase1无依赖可并行，Phase2为后续重构提供安全网，Phase3做代码质量提升，Phase4动架构。每阶段完成后跑全量测试验证无退化。

**Tech Stack:** Python 3.14, pytest, ruff

**当前基线:** 204 tests, all passing (v3.5.0, engine/__init__ 标记为 v3.6.0)

**v3.6.0 新增内容:**
- `engine/intelligence/ner.py` — 中文NER(零外部API), 89行
- `engine/theories/analytics.py` — 分析模式引擎增强, +121行
- `engine/formalize.py` — 形式化提取增强, +126行
- `engine/cli.py` — pipeline mode参数(未提交)
- README.md 仍写着 v3.1, pyproject.toml 仍写着 v3.5.0

---

## 阶段总览

| 阶段 | 内容 | 预估工作量 | 风险 |
|------|------|-----------|------|
| Phase 1 | P0/P1 快速修复 + 版本同步 | 小 (6-10文件) | 低 |
| Phase 2 | 测试覆盖补齐(含NER新模块) | 中 (8-12测试文件) | 低 |
| Phase 3 | 代码质量重构 | 中 (10-15文件修改) | 中 |
| Phase 4 | 架构分层整改 | 小 (3-5文件) | 高 |

**执行顺序:** Phase1 → Phase2 → Phase3 → Phase4
**每阶段完成必须**: 全量测试通过 + ruff无新增错误

---

## Phase 1: P0/P1 快速修复

### Task 1.1: 修复 pyproject.toml 打包配置

**Files:**
- Modify: `pyproject.toml:37-39`

**问题:** `packages = ["engine", "engine.toolforge", "engine.ontolang", "engine.ecosystem"]` 缺了 `engine.core`、`engine.foundation`、`engine.intelligence`、`engine.reasoners`、`engine.theories` 5个子包。pip install后CLI跑不起来。

- [ ] **Step 1: 替换为 find 自动发现**

将 `[tool.setuptools] packages` 改为 `[tool.setuptools.packages.find]`：

```toml
[tool.setuptools.packages.find]
include = ["engine*"]
```

删除原来的 `packages = [...]` 行。

- [ ] **Step 2: 验证安装**

```bash
cd /tmp && python3 -m venv test_venv && test_venv/bin/pip install /Users/xiamingxing/Workspace/ontoderive/ -q && test_venv/bin/ontoderive --help
```

期待输出: 正常显示CLI帮助信息，不报 `ModuleNotFoundError`

- [ ] **Step 3: 跑全量测试确认无退化**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && .venv/bin/python -m pytest tests/ -x -q
```

期待输出: `204 passed`


### Task 1.2: 删除死模块 `engine/ontolang/`

**Files:**
- Delete: `engine/ontolang/__init__.py`, `engine/ontolang/ast.py`, `engine/ontolang/parser.py`, `engine/ontolang/semantic.py`, `engine/ontolang/codegen.py`
- Modify: `pyproject.toml` (packages.find 自动跳过)
- Check: `tests/test_ontolang.py`

**问题:** 5个文件~500行的完整解析器/AST/代码生成管线，零个engine模块import它。`theories/ontolang.py` 提供了竞争的 `OntoLangParser`。

- [ ] **Step 1: 确认无外部引用**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "from engine.ontolang" --type py || echo "EXTERNAL_REF_NONE"
rg "import engine\.ontolang" --type py || echo "EXTERNAL_REF_NONE"
```

确认以上命令不输出任何engine/下的文件引用。

- [ ] **Step 2: 删除ontolang目录**

```bash
rm -rf engine/ontolang/
```

- [ ] **Step 3: 删除测试文件**

```bash
rm tests/test_ontolang.py
```

- [ ] **Step 4: 清理 `engine/__init__.py` 中ontolang的引用**

检查 `engine/__init__.py` 中是否有ontolang的导入，有则删除。

```bash
rg "ontolang" engine/__init__.py
```

- [ ] **Step 5: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```

期待: 196 passed (减掉8个ontolang测试)


### Task 1.3: 删除死模块 `engine/ecosystem/`

**Files:**
- Delete: `engine/ecosystem/__init__.py`, `engine/ecosystem/agora.py`, `engine/ecosystem/sophia.py`, `engine/ecosystem/minerva.py`, `engine/ecosystem/eidos_adapter.py`, `engine/ecosystem/ecos.py`
- Check: `tests/test_ecosystem.py`, `tests/test_eidos_adapter.py`

**问题:** 5个适配器文件~300行，零个engine模块import，仅测试文件引用。

- [ ] **Step 1: 确认无外部引用**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "from engine.ecosystem" --type py || echo "EXTERNAL_REF_NONE"
rg "import engine\.ecosystem" --type py || echo "EXTERNAL_REF_NONE"
```

- [ ] **Step 2: 删除ecosystem目录**

```bash
rm -rf engine/ecosystem/
```

- [ ] **Step 3: 删除对应测试文件**

```bash
rm tests/test_ecosystem.py tests/test_eidos_adapter.py
```

- [ ] **Step 4: 清理 `engine/__init__.py` 中ecosystem的引用**

```bash
rg "ecosystem" engine/__init__.py
```

- [ ] **Step 5: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```

期待: 181 passed (减掉ontolang 8 + ecosystem 7 + eidos_adapter 7 = 22个测试)


### Task 1.4: 修复 cli.py 硬编码绝对路径 + 清理 pipeline mode 临时逻辑

**Files:**
- Modify: `engine/cli.py:135-157`

**问题:** `sys.path.insert(0, "/Users/xiamingxing/Workspace/eidos/src")` 是开发者本地路径。同时已有一个未提交的pipeline mode临时逻辑(`--pipeline-output`)，需要纳入重构。

- [ ] **Step 1: 删除Eidos硬编码路径，改为无害化处理**

因为ecosystem在Task 1.3已删除，eidos_adapter不存在了。将整个Eidos处理块替换为:

```python
if getattr(args, "eidos", False):
    print("[eidos] Eidos 导出在 v3.6.0 已移除 (ecosystem 模块已清理)")
```

- [ ] **Step 2: Pipeline mode临时代码暂不动，留给后续重构**

当前 `--pipeline-output` 是一个占位桩（直接返回空结果），不影响主流程。在Task 3.4 (derive()拆解) 之前保留。

- [ ] **Step 3: 确认cli.py不再有绝对路径和不可用import**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "/Users/" engine/cli.py || echo "HARDCODED_PATH_CLEAN"
rg "import engine\.ecosystem" engine/cli.py || echo "ECOSYSTEM_REF_CLEAN"
```

- [ ] **Step 4: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 1.5: 改进 conftest.py 测试基础设施

**Files:**
- Modify: `tests/conftest.py`

**问题:** 缺临时目录fixture和mock LLM fixture

- [ ] **Step 1: 在conftest.py末尾添加fixtures**

```python
@pytest.fixture
def tmp_project(tmp_path):
    """创建临时OntoDerive项目"""
    for d in ["facts", "entities", "inferences", "protocols", "scheme", "_logs"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "facts" / "data.md").write_text(
        "| 编号 | 数据 | 数值 | 来源 |\n|------|------|------|------|\n| D-F1 | 测试事实 | 100 | 测试 |\n"
    )
    (tmp_path / "facts" / "policy.md").write_text(
        "| 编号 | 政策 | 发布主体 | 日期 |\n|------|------|---------|------|\n| P-F1 | 测试政策 | 测试 | 2024 |\n"
    )
    return tmp_path


@pytest.fixture
def mock_facts():
    """返回标准测试用事实字典"""
    return {
        "D-F1": {"desc": "测试事实A", "value": "100"},
        "D-F2": {"desc": "测试事实B", "value": "200"},
    }


@pytest.fixture
def mock_inferences():
    """返回标准测试用推论字典"""
    return {
        "INF-L1": {
            "text": "## 推论测试\nconfidence: high\n结论: 这是一个测试推论\n",
            "derives_from": ["D-F1", "D-F2"],
        },
    }
```

- [ ] **Step 2: 跑测试确认fixture可加载**

```bash
.venv/bin/python -m pytest tests/ --fixtures -q 2>&1 | grep -E "tmp_project|mock_facts|mock_inferences" || echo "FIXTURES_MISSING"
```

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 1.6: 修复测试中的硬编码 `/tmp/test` 路径

**Files:**
- Modify: `tests/test_ecosystem.py`, `tests/test_integration.py`

（注意：ecosystem在1.3已删除，只检查 `test_integration.py`）

**问题:** 测试中有硬编码 `/tmp/test` 路径，在并行CI环境会冲突。

- [ ] **Step 1: 查找硬编码路径**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg '/tmp/' tests/
```

- [ ] **Step 2: 将 `/tmp/` 路径替换为 `tmp_path` fixture**

对每个匹配的文件，将 `/tmp/test_*` 等路径改为 `tmp_path` fixture参数。具体修改见文件内容。

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 1.7: 同步版本号不一致

**Files:**
- Modify: `pyproject.toml:3`, `README.md:1`, `engine/cli.py:102`

**问题:** 同一项目版本号三处不一致:
- `README.md` 标题: v3.1
- `pyproject.toml`: 3.5.0
- `engine/__init__.py`: 3.6.0 (正确)
- `engine/cli.py:24`: 3.6.0 (正确)

目标: 统一为 v3.6.0

- [ ] **Step 1: 修改 pyproject.toml**

将 `version = "3.5.0"` 改为 `version = "3.6.0"`

- [ ] **Step 2: 修改 README.md**

```bash
cd /Users/xiamingxing/Workspace/ontoderive
sed -i '' 's/v3\.1-/v3.6.0-/' README.md
sed -i '' 's/version-3\.5\.0-blue/version-3.6.0-blue/' README.md
```

- [ ] **Step 3: 确认统一**

```bash
cd /Users/xiamingxing/Workspace/ontoderive
echo "pyproject:" && grep "^version" pyproject.toml
echo "README head:" && head -1 README.md
echo "__init__:" && grep "__version__" engine/__init__.py
```

- [ ] **Step 4: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


## Phase 2: 测试覆盖补齐

### Task 2.1: 给 reasoners/reasoner.py 写测试

**Files:**
- Create: `tests/test_reasoner.py`

**问题:** reasoner.py是整个项目第二热的模块(52处引用)，0测试。核心类 `RuleReasoner` 有21种推理方法。

- [ ] **Step 1: 写测试文件**

```python
"""Tests for RuleReasoner — 规则推导引擎"""
import pytest
from engine.reasoners.reasoner import RuleReasoner, DerivationRule


def test_default_rules_loaded():
    r = RuleReasoner()
    assert len(r.rules) >= 5
    assert r._default_rules()[0].name == "numeric_comparison"


def test_derive_empty_inputs():
    r = RuleReasoner()
    results = r.derive({}, {})
    assert isinstance(results, list)
    assert r.state == "done"


def test_derive_numeric_comparison():
    r = RuleReasoner()
    facts = {"D-F1": {"desc": "人数", "value": "100"}, "D-F2": {"desc": "人数", "value": "200"}}
    results = r.derive(facts, {})
    types = [res["type"] for res in results]
    assert "numeric_comparison" in types


def test_missing_reference_detected():
    r = RuleReasoner()
    infs = {"INF-L1": {"text": "test", "derives_from": ["D-F999"]}}
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "missing_reference" in types


def test_shared_premise_detected():
    r = RuleReasoner()
    infs = {
        "INF-A": {"text": "test", "derives_from": ["D-F1", "D-F2", "D-F3"]},
        "INF-B": {"text": "test", "derives_from": ["D-F1", "D-F2", "D-F4"]},
    }
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "shared_premise" in types


def test_coverage_analysis():
    r = RuleReasoner()
    facts = {"D-F1": {}, "D-F2": {}, "D-F3": {}}
    infs = {"INF-L1": {"text": "test", "derives_from": ["D-F1"]}}
    results = r.derive(facts, infs)
    types = [res["type"] for res in results]
    assert "coverage" in types


def test_threshold_alert():
    r = RuleReasoner()
    facts = {"D-F1": {"desc": "测试覆盖率", "value": "30"}}
    results = r.derive(facts, {})
    types = [res["type"] for res in results]
    assert "threshold_alert" in types


def test_chain_break_detected():
    r = RuleReasoner()
    infs = {"INF-L2": {"text": "test", "derives_from": ["INF-L1"]}}
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "chain_break" in types


def test_relation_reasoning():
    r = RuleReasoner()
    relations = [
        {"subject": "ORG-A", "relation_type": "employs", "object": "ROL-X"},
        {"subject": "ROL-X", "relation_type": "employs", "object": "ROL-Y"},  # 域约束违规
    ]
    results = r.derive({}, {}, relations)
    assert isinstance(results, list)


def test_influence_analysis():
    r = RuleReasoner()
    infs = {
        "INF-L1": {"text": "test", "derives_from": ["D-F1"]},
        "INF-L2": {"text": "test", "derives_from": ["D-F1"]},
        "INF-L3": {"text": "test", "derives_from": ["D-F1"]},
    }
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "influence_analysis" in types


def test_redundancy_check():
    r = RuleReasoner()
    infs = {
        "INF-A": {"text": "test", "derives_from": ["D-F1", "D-F2", "D-F3"]},
        "INF-B": {"text": "test", "derives_from": ["D-F1", "D-F2", "D-F3"]},
    }
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "redundancy_warning" in types


def test_evidence_gap():
    r = RuleReasoner()
    infs = {"INF-L1": {"text": "test", "derives_from": ["D-F1"]}}
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "evidence_gap" in types


def test_case_based_reasoning():
    r = RuleReasoner()
    project = {"facts": {"D-F1": {"desc": "人数", "value": "100"}}, "inferences": {}}
    cases = [{"name": "参考案例A", "facts": {"D-F1": {"desc": "人数", "value": "50"}}, "inferences": {}, "outcome": "成功"}]
    results = r.case_based_reasoning(project, cases)
    assert isinstance(results, list)
    # 相似度 > 0.3 会匹配
    assert any("相似度" in str(r) for r in results)


def test_incremental_recalc():
    r = RuleReasoner()
    old = {"D-F1": {"value": "100"}}
    new = {"D-F1": {"value": "200"}}
    infs = {"INF-L1": {"text": "test", "derives_from": ["D-F1"]}}
    results = r.incremental_recalc(old, new, infs)
    assert len(results) == 1
    assert results[0]["type"] == "incremental_recalc"


def test_temporal_reasoning():
    r = RuleReasoner()
    facts = {
        "D-F1": {"desc": "2020年数据", "value": "100"},
        "D-F2": {"desc": "2023年数据", "value": "200"},
    }
    results = r.temporal_reasoning(facts)
    assert len(results) >= 1
    assert results[0]["type"] == "temporal_sequence"


def test_consistency_analysis():
    r = RuleReasoner()
    infs = {
        "INF-A": {"text": "confidence: high\n结论: 测试\n", "derives_from": []},
        "INF-B": {"text": "confidence: high\n结论: 测试\n", "derives_from": []},
        "INF-C": {"text": "confidence: high\n结论: 测试\n", "derives_from": []},
    }
    results = r.derive({}, infs)
    types = [res["type"] for res in results]
    assert "consistency_warning" in types
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_reasoner.py -v
```

期待: 全部PASS

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.2: 给 reasoners/unified_reasoner.py 和 reasoning.py 写测试

**Files:**
- Create: `tests/test_unified_reasoner.py`

- [ ] **Step 1: 写测试**

```python
"""Tests for UnifiedReasoner + ReasoningSelector + ContentCanonicalizer"""
import pytest
from engine.reasoners.unified_reasoner import UnifiedReasoner, UnifiedConclusion
from engine.reasoners.reasoning import ReasoningSelector, ContentCanonicalizer, DataProfile


class TestUnifiedConclusion:
    def test_to_dict(self):
        uc = UnifiedConclusion(conclusion="测试", certainty="certain", method="numeric_comparison")
        d = uc.to_dict()
        assert d["conclusion"] == "测试"
        assert d["type"] == "numeric_comparison"


class TestUnifiedReasoner:
    def test_reason_empty(self):
        ur = UnifiedReasoner()
        results = ur.reason({}, {})
        assert isinstance(results, list)

    def test_reason_with_facts(self):
        ur = UnifiedReasoner()
        facts = {"D-F1": {"desc": "人数", "value": "100"}, "D-F2": {"desc": "人数", "value": "200"}}
        results = ur.reason(facts, {})
        types = [r.method for r in results]
        assert "numeric_comparison" in types

    def test_summary(self):
        ur = UnifiedReasoner()
        ur.reason({"D-F1": {"desc": "人数", "value": "100"}}, {})
        s = ur.summary()
        assert "total" in s
        assert "by_source" in s


class TestContentCanonicalizer:
    def test_canonicalize_facts(self):
        cc = ContentCanonicalizer()
        raw = {"D-F1": {"desc": "人数", "value": "100人"}}
        result = cc.canonicalize_facts(raw)
        assert result["D-F1"]["structured_value"] == 100.0
        assert result["D-F1"]["has_numeric"] is True

    def test_canonicalize_facts_timestamp(self):
        cc = ContentCanonicalizer()
        raw = {"D-F1": {"desc": "2023年数据", "value": "100"}}
        result = cc.canonicalize_facts(raw)
        assert result["D-F1"]["has_timestamp"] is True

    def test_canonicalize_inferences(self):
        cc = ContentCanonicalizer()
        raw = {"INF-L1": {"text": "confidence: high\n结论: 测试结论\n", "derives_from": ["D-F1"]}}
        result = cc.canonicalize_inferences(raw)
        assert result["INF-L1"]["derives_from"] == ["D-F1"]
        assert result["INF-L1"]["confidence_value"] == 0.92
        assert result["INF-L1"]["conclusion"] == "测试结论"


class TestReasoningSelector:
    def test_profile_empty(self):
        rs = ReasoningSelector()
        p = rs.profile({}, {})
        assert p.fact_count == 0
        assert p.inf_count == 0

    def test_profile_with_data(self, mock_facts, mock_inferences):
        rs = ReasoningSelector()
        p = rs.profile(mock_facts, mock_inferences)
        assert p.fact_count == 2
        assert p.inf_count == 1

    def test_select_rules(self):
        rs = ReasoningSelector()
        p = DataProfile(has_numeric=True, fact_count=1, inf_count=1)
        selected = rs.select_rules(p)
        assert "numeric_comparison" in selected
        assert "coverage_analysis" in selected

    def test_explain_selection(self):
        rs = ReasoningSelector()
        p = DataProfile(fact_count=5, inf_count=3, has_numeric=True)
        explanation = rs.explain_selection(p)
        assert "数据画像" in explanation
        assert "激活规则" in explanation
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_unified_reasoner.py -v
```

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.3: 给 reasoners/reasoner_formal.py 写测试

**Files:**
- Create: `tests/test_reasoner_formal.py`

- [ ] **Step 1: 写测试**

```python
"""Tests for FormalReasoner — 形式推理引擎"""
import pytest
from engine.reasoners.reasoner_formal import FormalReasoner, FormalConclusion


class TestFormalConclusion:
    def test_defaults(self):
        fc = FormalConclusion(conclusion="测试", certainty="certain", method="subsumption")
        assert fc.confidence == 0.90
        assert fc.derives_from == []


class TestFormalReasoner:
    def test_reason_empty(self):
        fr = FormalReasoner()
        # 创建一个最小化的knowledge对象
        class DummyKnowledge:
            class Abox:
                facts = {}
                entities = {}
            class Tbox:
                def get(self, k, d=None):
                    return {}
            abox = Abox()
            tbox = Tbox()
            inferences = []

        results = fr.reason(DummyKnowledge())
        assert isinstance(results, list)

    def test_summary_empty(self):
        fr = FormalReasoner()
        s = fr.summary()
        assert s["total"] == 0
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_reasoner_formal.py -v
```

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.4: 给 pipeline_v4.py 写测试

**Files:**
- Create: `tests/test_pipeline_v4.py`

**问题:** pipeline_v4.py是顶层的四阶段管线文件，0测试。

- [ ] **Step 1: 写测试**

```python
"""Tests for FormalPipeline — 四阶段形式化推理管线"""
import pytest
from engine.pipeline_v4 import FormalPipeline


def test_pipeline_creates():
    p = FormalPipeline()
    assert p is not None


def test_pipeline_run_empty():
    p = FormalPipeline()
    result = p.run("")
    assert isinstance(result, dict)
    assert "report" in result
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_pipeline_v4.py -v
```

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.5: 给 core/export.py 写测试

**Files:**
- Create: `tests/test_export.py`

- [ ] **Step 1: 写测试**

```python
"""Tests for export — 导出模块"""
import pytest
from engine.core.export import to_html, to_json, to_markdown


@pytest.fixture
def sample_summary():
    return {
        "facts": 5,
        "entities": 3,
        "inferences": 2,
        "derived_conclusions": [
            {
                "source": "rule_engine",
                "derivation_trail": "R1: D-F1→D-F2",
                "conclusion": "测试结论A大于测试结论B",
                "confidence": 0.95,
            },
        ],
        "derivation_hints": ["测试提示1"],
        "confidence_distribution": {"mean": 0.85, "min": 0.7, "max": 0.95},
    }


def test_to_html(sample_summary):
    html = to_html(sample_summary, "test-project")
    assert "<!DOCTYPE html>" in html
    assert "test-project" in html
    assert "测试结论A" in html
    assert "95%" in html


def test_to_json(sample_summary):
    import json
    js = to_json(sample_summary)
    parsed = json.loads(js)
    assert parsed["facts"] == 5
    assert parsed["entities"] == 3


def test_to_markdown(sample_summary):
    md = to_markdown(sample_summary, "test")
    assert "OntoDerive" in md
    assert "测试结论A" in md
    assert "95%" in md
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_export.py -v
```

- [ ] **Step 3: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.6: 给 intelligence/ 关键模块写测试

**Files:**
- Create: `tests/test_insight.py`, `tests/test_judge.py`, `tests/test_ner.py`

- [ ] **Step 1: 写 intelligence/insight.py 测试**

```python
"""Tests for InsightEngine"""
import pytest
from pathlib import Path
from engine.intelligence.insight import InsightEngine, Insight


class TestInsight:
    def test_to_dict(self):
        ins = Insight(insight="测试洞察", source="test", confidence=0.85, model="test")
        d = ins.to_dict()
        assert d["insight"] == "测试洞察"
        assert d["confidence"] == 0.85

    def test_str(self):
        ins = Insight(insight="测试洞察", source="test", confidence=0.85, model="test")
        s = str(ins)
        assert "测试洞察" in s


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

    def test_save_insights_empty(self, tmp_project):
        engine = InsightEngine()
        engine.project_root = tmp_project
        engine.save_insights(tmp_project / "_logs")
        assert (tmp_project / "_logs" / "insights.json").exists()
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_insight.py -v
```

- [ ] **Step 3: 跑全量测试确认无退化**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.7: 给新模块 intelligence/ner.py 写测试 (v3.6.0新增)

**Files:**
- Create: `tests/test_ner.py`

**问题:** NER模块是v3.6.0新增的纯规则中文命名实体识别，0测试。代码简单(89行)，但规则匹配逻辑需要覆盖多种场景。

- [ ] **Step 1: 写测试**

```python
"""Tests for NER — 中文命名实体识别"""
import pytest
from engine.intelligence.ner import extract_entities, _extract_entities_by_suffix


class TestExtractBySuffix:
    def test_org_suffix(self):
        result = _extract_entities_by_suffix("中关村科技园区", ("园区",), "ORG")
        assert len(result) > 0
        assert any("科技园区" in name or "中关村科技园区" in name for name, _ in result)

    def test_role_suffix(self):
        result = _extract_entities_by_suffix("张三经理", ("经理",), "ROL")
        assert len(result) > 0
        names = [name for name, _ in result]
        assert any("经理" in n for n in names)

    def test_loc_suffix(self):
        result = _extract_entities_by_suffix("北京市", ("市",), "ORG")
        assert len(result) > 0
        assert any("北京" in name for name, _ in result)


class TestExtractEntities:
    def test_empty_text(self):
        assert extract_entities("") == []

    def test_short_text(self):
        """不足3字的文本不应产生实体"""
        result = extract_entities("的")
        assert isinstance(result, list)

    def test_org_matching(self):
        """文本中出现组织名后缀应提取"""
        result = extract_entities("北京大学在量子计算领域取得突破", use_jieba=False)
        names = [name for name, _ in result]
        assert len(names) > 0

    def test_role_matching(self):
        result = extract_entities("这项成果由李教授带领团队完成", use_jieba=False)
        names = [name for name, _ in result]
        assert len(names) > 0

    def test_deduplication(self):
        result = extract_entities("北京大学和北京大学医学部", use_jieba=False)
        names = [name for name, _ in result]
        assert len(names) == len(set(names))  # 无重复

    def test_use_jieba_fallback_on_error(self):
        """即使use_jieba=True但jieba不可用, 应平滑回退规则模式"""
        result = extract_entities("清华大学", use_jieba=True)
        assert isinstance(result, list)
```

- [ ] **Step 2: 跑测试**

```bash
.venv/bin/python -m pytest tests/test_ner.py -v
```

- [ ] **Step 3: 跑全量测试确认无退化**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 2.8: 检查所有未覆盖模块，评估是否需写测试

**Files:**
- Review: `tests/` 各文件

- [ ] **Step 1: 列出当前覆盖状态**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && echo "=== engine modules without test files ===" && for f in $(find engine -name "*.py" ! -name "__init__.py"); do mod=$(echo "$f" | sed 's|engine/||;s|/|_|g;s|\.py||'); test_file="tests/test_${mod}"; if [ ! -f "$test_file" ]; then echo "  NO_TEST: $f"; fi; done
```

- [ ] **Step 2: 对剩余的未覆盖模块评估是否需要测试**

以下是可能还需要测的：

| 模块 | 优先级 | 说明 |
|------|--------|------|
| `engine/core/check_theory.py` | P3 | 目前被core测试间接覆盖，可接受 |
| `engine/foundation/protocols.py` | P3 | 接口定义，被测试间接覆盖 |
| `engine/foundation/rule_loader.py` | P2 | 建议加基础测试 |
| `engine/foundation/ontology_map.py` | P3 | 被其他测试间接覆盖 |
| `engine/intelligence/got.py` | P3 | 需要LLM后端，暂时跳过 |
| `engine/intelligence/react.py` | P3 | 同上 |
| `engine/intelligence/semantic.py` | P3 | 3行re-export，跳过 |
| `engine/intelligence/prompts.py` | P3 | prompt模板，跳过 |
| `engine/reasoners/reasoning.py` | 已在2.2中覆盖 |

如有时间，给 `rule_loader.py` 补测试:

```python
"""Tests for RuleLoader"""
import pytest
from engine.foundation.rule_loader import RuleLoader


def test_rule_loader_create():
    rl = RuleLoader()
    assert rl.rules == []


def test_rule_loader_to_conclusion():
    rule = {"id": "TEST-R1", "name": "测试规则", "description": "测试", "condition": "True", "conclusion": "测试结论", "confidence": 0.8}
    c = RuleLoader.to_conclusion(rule)
    assert c["conclusion"] == "测试结论"
    assert c["type"] == "yaml_rule"
```

- [ ] **Step 3: 最终全量验证**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


## Phase 3: 代码质量重构

### Task 3.1: 修复所有 broad `except Exception:` 吞噬

**Files:**
- Modify: `engine/intelligence/llm.py`, `engine/core/derive.py`, `engine/pipeline_v4.py`, `engine/theories/logic.py`, `engine/reasoners/unified_reasoner.py`

**问题:** 10+处 `except Exception: pass` 或 `except Exception: return None`，隐藏真实错误。

- [ ] **Step 1: 修复 intelligence/llm.py 中6处 except**

将:

```python
except Exception:
    return None
```

改为具体异常类型:

```python
except (ConnectionError, TimeoutError, json.JSONDecodeError) as e:
    import sys; print(f"[llm] 连接/解析失败: {e}", file=sys.stderr)
    return None
```

具体的修改:

```python
# 第41行附近: HTTP请求
# 改为:
except (ConnectionError, TimeoutError) as e:

# 第47行附近: JSON解析
# 改为:
except json.JSONDecodeError as e:

# 第74-75行: API调用
# 改为:
except (ConnectionError, TimeoutError, ValueError) as e:

# 第103行: 模型响应
# 改为:
except (KeyError, IndexError, TypeError) as e:

# 第124-125行: 缓存
# 改为:
except (IOError, OSError) as e:

# 第137行: 兜底
# 改为:
except Exception as e:
    import sys; print(f"[llm] 未知错误: {e}", file=sys.stderr)
    return None  # 保留一个兜底但打印错误
```

- [ ] **Step 2: 修复 derive.py 中4处 except**

```python
# 第90-91行 (Bayesian skip)
# 改为:
except ImportError as e:
    import sys; print(f"[derive] Bayesian不可用: {e}", file=sys.stderr)

# 第97-98行 (Logic skip)
# 改为:
except ImportError as e:
    import sys; print(f"[derive] Logic不可用: {e}", file=sys.stderr)

# 第128行 (DAG分析)
# 改为:
except Exception as e:
    import sys; print(f"[derive] DAG分析失败: {e}", file=sys.stderr)

# 第167行 (UnifiedReasoner)
# 改为:
except Exception as e:
    import sys; print(f"[derive] UnifiedReasoner不可用: {e}", file=sys.stderr)
```

- [ ] **Step 3: 修复 unified_reasoner.py 第100行**

```python
# 改为:
except ImportError as e:
    import sys; print(f"[unified] analytics模块不可用: {e}", file=sys.stderr)
```

- [ ] **Step 4: 跑全量测试确认无退化**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 3.2: 去重事实/推论扫描逻辑

**Files:**
- Modify: `engine/foundation/utils.py` (新增), `engine/core/derive.py` (复用), `engine/theories/bayesian.py` (复用), `engine/theories/logic.py` (复用)

**问题:** 3个文件各自独立实现了同样的Markdown表格正则扫描 `D-F\d+` / `P-F\d+` / `INF-` 模式。改格式要改3处。

- [ ] **Step 1: 在 foundation/utils.py 中新增共享函数**

在文件末尾添加:

```python
import re

def scan_facts_from_md(text: str) -> dict:
    """从Markdown表格中扫描事实数据 (D-F / P-F)"""
    facts = {"data": {}, "policy": {}}
    for m in re.finditer(r'\| (D-F\d+)\s*\|([^|]+)\|([^|]+)\|', text):
        facts["data"][m.group(1)] = {"desc": m.group(2).strip(), "value": m.group(3).strip()}
    for m in re.finditer(r'\| (P-F\d+)\s*\|([^|]+)\|', text):
        facts["policy"][m.group(1)] = {"desc": m.group(2).strip()}
    return facts


def scan_inferences_from_md(text: str) -> dict:
    """从Markdown中扫描推论块 (INF-)"""
    inferences = {}
    for block in re.split(r'^##\s+', text, flags=re.MULTILINE)[1:]:
        title = block.strip().split('\n')[0].strip()
        df_line = re.search(r'derives_from:\s*\[([^\]]+)\]', block)
        df = re.findall(r'(D-F\d+|P-F\d+|INF-[\w\d]+)', df_line.group(1)) if df_line else []
        inferences[title] = {"derives_from": list(set(df)), "text": block[:300]}
    return inferences
```

- [ ] **Step 2: 在 derive.py 中复用 scan_facts_from_md**

将:

```python
facts = {"data": {}, "policy": {}}
for f in all_md(self.facts_dir):
    text = rf(f)
    for m in re.finditer(r'\| (D-F\d+)\s*\|([^|]+)\|([^|]+)\|', text):
        facts["data"][m.group(1)] = {"desc": m.group(2).strip(), "value": m.group(3).strip()}
    for m in re.finditer(r'\| (P-F\d+)\s*\|([^|]+)\|', text):
        facts["policy"][m.group(1)] = {"desc": m.group(2).strip()}
```

改为:

```python
from engine.foundation.utils import scan_facts_from_md
facts = {"data": {}, "policy": {}}
for f in all_md(self.facts_dir):
    result = scan_facts_from_md(rf(f))
    facts["data"].update(result["data"])
    facts["policy"].update(result["policy"])
```

同理，将 `derive.py` 中扫描推论的代码替换为 `scan_inferences_from_md`。

- [ ] **Step 3: 在 bayesian.py 和 logic.py 中做同样替换**

将各自文件中的同类正则扫描替换为调用 `scan_facts_from_md` / `scan_inferences_from_md`。

- [ ] **Step 4: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```

确认仍然是 181+ passed (具体取决于 Phase1/2 之后的测试数)


### Task 3.3: 消除 try/except import 模板代码

**Files:**
- Modify: `engine/core/derive.py`, `engine/core/check.py`, `engine/theories/bayesian.py`, `engine/theories/logic.py`, `engine/theories/metrics.py`, `engine/theories/controller.py`, `engine/theories/turing_k.py`

**问题:** ~8个文件都有这段样板:

```python
try:
    from .utils import rf, wf, all_md
except ImportError:
    from engine.foundation.utils import rf, wf, all_md  # noqa
```

- [ ] **Step 1: 在每个文件中统一替换为直引形式**

所有文件统一改为:

```python
from engine.foundation.utils import rf, wf, all_md, load_json, save_json
```

因为 `engine/__init__.py` 在顶部做了 `sys.path.insert(0, ...)`，且pip安装后engine在包路径中，直接 `from engine.foundation.utils` 在所有场景下都有效。

具体的文件列表和要改的行:

**derive.py:**
```python
# 删除:
try:
    from .utils import rf, wf, all_md, load_json, save_json
except ImportError:
    from engine.foundation.utils import rf, wf, all_md, load_json, save_json  # noqa
# 替换为:
from engine.foundation.utils import rf, wf, all_md, load_json, save_json
```

其他文件同理。保留 `from .protocols import ...` 的 try/except 直到 Phase 4。

- [ ] **Step 2: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 3.4: 拆分 derive() 大方法

**Files:**
- Modify: `engine/core/derive.py`

**问题:** `OntoDerive.derive()` 116行，做5件事（事实扫描、贝叶斯、逻辑图、DAG分析、统一推理），4个try/except块。

- [ ] **Step 1: 抽取子方法**

将 derive() 拆分为:

```python
def derive(self):
    """正向推导 — 事实扫描 + 多引擎推理"""
    summary = self._derive_baseline()      # 扫描事实+实体+推论
    self._derive_bayesian(summary)         # 贝叶斯置信度
    self._derive_entailment(summary)       # 逻辑图分析
    hints = self._derive_hints()           # 内容推导 + DAG分析
    if hints:
        summary["derivation_hints"] = hints[:15]
    self._derive_unified(summary)          # 统一推理
    save_json(self.log_dir / "derive-summary.json", summary)
    self._print_summary(summary)
    return summary


def _derive_baseline(self):
    """1. 事实基座扫描"""
    facts = {"data": {}, "policy": {}}
    for f in all_md(self.facts_dir):
        result = scan_facts_from_md(rf(f))
        facts["data"].update(result["data"])
        facts["policy"].update(result["policy"])

    entities = {}
    for f in all_md(self.entities_dir):
        for m in re.finditer(r'\*\*(ORG-[\w-]+|ROL-[\w-]+|PRJ-[\w-]+|DOC-[\w-]+|STD-[\w-]+)\*\*', rf(f)):
            entities[m.group(1)] = True

    infer_count = 0
    for f in all_md(self.inferences_dir):
        infer_count += len(re.findall(r'^##\s+INF-', rf(f), re.MULTILINE))

    return {
        "derived_at": datetime.datetime.now().isoformat(),
        "facts": len(facts["data"]) + len(facts["policy"]),
        "entities": len(entities),
        "inferences": infer_count,
        "scheme_files": len(all_md(self.scheme_dir)),
    }


def _derive_bayesian(self, summary):
    """2. 贝叶斯置信度传播"""
    try:
        from engine.theories.bayesian import BayesianLayer
        bl = BayesianLayer(self.root)
        _, bayes_infs = bl.propagate_all()
        confs = [i.get("propagated_confidence", i.get("base_confidence", 0.85)) for i in bayes_infs.values()]
        if confs:
            summary["confidence_distribution"] = {
                "mean": round(sum(confs)/len(confs), 4),
                "min": round(min(confs), 4),
                "max": round(max(confs), 4),
                "count": len(confs),
            }
    except ImportError as e:
        import sys; print(f"[derive] Bayesian不可用: {e}", file=sys.stderr)


def _derive_entailment(self, summary):
    """3. 逻辑依赖图分析"""
    try:
        from engine.theories.logic import build_from_project
        g = build_from_project(self.root).stats()
        summary["entailment_graph"] = {
            "nodes": g["nodes"], "edges": g["edges"],
            "max_depth": g["max_depth"], "cycles": g["cycles"],
        }
    except ImportError as e:
        import sys; print(f"[derive] Logic不可用: {e}", file=sys.stderr)


def _derive_hints(self):
    """4. 内容推导 + DAG矛盾检测"""
    hints = []
    for f in all_md(self.inferences_dir):
        text = rf(f)
        if "derives_from" not in text:
            hints.append(f"{f.name}: 缺少 derives_from 声明")
        if "理论支撑" not in text and "理论" not in text:
            hints.append(f"{f.name}: 建议添加理论支撑")
    for f in all_md(self.scheme_dir):
        text = rf(f)
        if len(re.findall(r'D-F\d+|P-F\d+', text)) == 0:
            hints.append(f"{f.name}: 未引用任何事实编号")

    try:
        from engine.theories.logic import build_from_project
        g = build_from_project(self.root)
        st = g.stats()
        if st["contradictions"]:
            for c in st["contradictions"]:
                hints.append(
                    f"矛盾: {c['inference_a']} vs {c['inference_b']} "
                    f"(共享事实{c['shared_facts']}, 对立词{c['opposing_terms']})")
        if st["max_depth"] < 2 and st["inferences"] >= 3:
            hints.append(f"推导链深度仅{st['max_depth']}，推论间缺少递进关系")
        if st["has_cycles"]:
            hints.append(f"检测到{st['cycles']}个循环引用")
    except Exception as e:
        import sys; print(f"[derive] DAG分析失败: {e}", file=sys.stderr)

    summary["analysis_mode"] = "structural"
    return hints


def _derive_unified(self, summary):
    """5. 统一推理引擎"""
    try:
        from engine.reasoners.unified_reasoner import UnifiedReasoner
        from engine.foundation.utils import scan_facts_from_md, scan_inferences_from_md

        facts = {"data": {}, "policy": {}}
        for f in all_md(self.facts_dir):
            result = scan_facts_from_md(rf(f))
            facts["data"].update(result["data"])
            facts["policy"].update(result["policy"])

        inferences_dict = {}
        for f in all_md(self.inferences_dir):
            inferences_dict.update(scan_inferences_from_md(rf(f)))

        relations = []
        for sf in all_md(self.scheme_dir):
            text = rf(sf)
            for m in re.finditer(
                r'[-*]\s+((?:ORG|ROL|PRJ|RES|DOC|STD)-[\w一-鿿-]+)'
                r'\s+(\w+)\s+'
                r'((?:ORG|ROL|PRJ|RES|DOC|STD)-[\w一-鿿-]+)',
                text
            ):
                relations.append({
                    "subject": m.group(1), "relation_type": m.group(2),
                    "object": m.group(3),
                })

        ur = UnifiedReasoner(loaded_rules=self._loaded_rules)
        uc_list = ur.reason(
            facts["data"], inferences_dict, relations=relations if relations else None,
            enhancer=self._try_llm()
        )
        summary["derived_conclusions"] = [uc.to_dict() for uc in uc_list[:25]]
    except ImportError as e:
        import sys; print(f"[derive] UnifiedReasoner不可用: {e}", file=sys.stderr)
    except Exception as e:
        import sys; print(f"[derive] 推理失败: {e}", file=sys.stderr)
```

- [ ] **Step 2: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 3.5: 硬编码模型名/URL → 配置化

**Files:**
- Modify: `engine/intelligence/llm.py`

**问题:** 默认模型名 `"qwopus3.6-35b-a3b-v1"` 和 `http://localhost:1234` 硬编码。

- [ ] **Step 1: 将默认值改为从环境变量读取**

```python
# 原:
DEFAULT_MODEL = "qwopus3.6-35b-a3b-v1"
DEFAULT_BASE_URL = "http://localhost:1234/v1"

# 改为:
import os
DEFAULT_MODEL = os.environ.get("ONTODERIVE_LLM_MODEL", "qwen2.5-14b")
DEFAULT_BASE_URL = os.environ.get("ONTODERIVE_LLM_BASE_URL", "http://localhost:11434/v1")
```

注意: 改用更通用的默认模型名 `qwen2.5-14b`，并默认使用Ollama端口 `11434`，因为这才是最常见的本地LLM部署方式。用户仍可通过环境变量覆盖。

- [ ] **Step 2: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 3.6: 为关键public方法补docstring

**Files:**
- Modify: `engine/core/derive.py` (derive/analyze/run_rounds), `engine/reasoners/unified_reasoner.py` (reason/summary), `engine/theories/bayesian.py` (propagate_all), `engine/theories/logic.py` (build_from_project), `engine/reasoners/reasoner.py` (derive/case_based_reasoning/incremental_recalc)

**问题:** 大部分public方法缺docstring。

- [ ] **Step 1: 逐一检查并补充**

只需要为 **public方法** 加一行简短的docstring，不要长篇大论。

示例:

```python
def derive(self):
    """正向推导 — 事实扫描+贝叶斯+逻辑图+DAG分析+统一推理"""
```

- [ ] **Step 2: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


## Phase 4: 架构分层整改

### Task 4.1: 修复分层反转 — 将 pipeline_v4.py 和 formalize.py 移动到正确层级

**Files:**
- Rename: `engine/pipeline_v4.py` → `engine/core/pipeline_v4.py` (或 `engine/reasoners/pipeline_v4.py`)
- Rename: `engine/formalize.py` → `engine/core/formalize.py` (或 `engine/foundation/formalize.py`)
- Modify: 所有 import 这两个模块的文件

**问题:** `pipeline_v4.py` 和 `formalize.py` 在 engine/ 顶层，却被子包 `core/derive.py` import。分层反转。

分析归属:
- `pipeline_v4.py` (四阶段管线: LLM提取→符号化→形式推理→解读) → 放到 `engine/reasoners/pipeline_v4.py`
- `formalize.py` (形式化提取: LLM分段→规则降级→ABox/TBox) → 放到 `engine/reasoners/formalize.py`

- [ ] **Step 1: 移动文件**

```bash
cd /Users/xiamingxing/Workspace/ontoderive/engine
cp pipeline_v4.py reasoners/pipeline_v4.py
cp formalize.py reasoners/formalize.py
```

- [ ] **Step 2: 更新所有引用点**

搜索所有 `from engine.pipeline_v4` 和 `from engine.formalize`:

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "from engine\.(pipeline_v4|formalize)" --type py
```

将每个引用改为 `from engine.reasoners.pipeline_v4` / `from engine.reasoners.formalize`。

涉及文件:
- `engine/core/derive.py`
- `engine/__init__.py`
- `engine/cli.py`
- `engine/mcp_server.py`

- [ ] **Step 3: 更新 `engine/reasoners/__init__.py` 导出**

```python
"""推理引擎层 — 21种推理模式 + 选择器 + 范式化 + 形式推理 + 统一推理 + 形式化管线"""
# ... 现有导入 ...
from engine.reasoners.pipeline_v4 import FormalPipeline
from engine.reasoners.formalize import Formalizer, FormalKnowledge
```

- [ ] **Step 4: 原地为兼容保留桩**

如果担心外部代码引用旧路径，在 engine/ 顶层保留桩文件:

**engine/pipeline_v4.py:**
```python
"""兼容桩 — 请使用 engine.reasoners.pipeline_v4"""
from engine.reasoners.pipeline_v4 import *  # noqa
```

**engine/formalize.py:**
```python
"""兼容桩 — 请使用 engine.reasoners.formalize"""
from engine.reasoners.formalize import *  # noqa
```

- [ ] **Step 5: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 4.2: 删除 intelligence/semantic.py 冗余shim文件

**Files:**
- Delete: `engine/intelligence/semantic.py`
- Modify: `engine/intelligence/__init__.py`

**问题:** `intelligence/semantic.py` 是一个仅2行的re-export桩(`from engine.foundation.semantic import SemanticMatcher`)。`intelligence/__init__.py` 已直接从 `foundation.semantic` 导入 `SemanticMatcher`。这个独立shim文件是冗余的，删除它。

- [ ] **Step 1: 删除 intelligence/semantic.py**

```bash
rm engine/intelligence/semantic.py
```

- [ ] **Step 2: 确认 intelligence/__init__.py 已有正确的导入**

```python
# 确认存在此行，无需修改:
from engine.foundation.semantic import SemanticMatcher
```

- [ ] **Step 3: 搜索是否有其他文件引用 `engine.intelligence.semantic`**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "from engine\.intelligence\.semantic" --type py || echo "NO_REF_CLEAN"
```

- [ ] **Step 4: 跑全量测试**

```bash
.venv/bin/python -m pytest tests/ -x -q
```


### Task 4.3: 评估 setup.py 删除

**Files:**
- Delete/keep: `setup.py`

**问题:** setup.py 只有一行 `setup()`，pyproject.toml已是权威配置。

- [ ] **Step 1: 确认无工具依赖 setup.py**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && rg "setup\.py" --type py || echo "NO_REF"
rg "python setup\.py" . || echo "NO_BUILD_CMD"
```

如果无引用，直接删除:

```bash
rm setup.py
```

- [ ] **Step 2: 确认pip install仍工作**

```bash
cd /tmp && rm -rf test_venv && python3 -m venv test_venv && test_venv/bin/pip install /Users/xiamingxing/Workspace/ontoderive/ -q && test_venv/bin/ontoderive --help
```


## 最终验证

### Task Final: 全量回归验证

- [ ] **Step 1: 跑全量测试**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && .venv/bin/python -m pytest tests/ -x -v
```

期待: 全部通过

- [ ] **Step 2: ruff lint检查**

```bash
cd /Users/xiamingxing/Workspace/ontoderive && ruff check engine/ tests/ --statistics
```

期待: 0 errors（或仅预存警告）

- [ ] **Step 3: 验证CLI正常启动**

```bash
.venv/bin/python -m engine.cli --help
.venv/bin/python -m engine.cli derive --project examples/z-park
```

两个命令都应正常执行

- [ ] **Step 4: 更新 README 统计**

如果测试数变化，更新 README.md 中的197→新数字

- [ ] **Step 5: 最终状态确认**

```bash
echo "=== 模块统计 ===" && find engine -name "*.py" ! -name "__init__.py" | wc -l
echo "=== 测试统计 ===" && .venv/bin/python -m pytest tests/ --collect-only -q 2>&1 | tail -1
```
