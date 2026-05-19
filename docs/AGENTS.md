# Agent可读操作手册 v3.2

> AI Agent加载此项目时的标准操作流程。

---

## Agent能力清单

| 操作 | 命令/代码 | 需要LLM吗 |
|------|----------|---------|
| 结构分析 | `od.derive()` | ❌ |
| 推导结论 | `summary["derived_conclusions"]` | ❌ |
| 规约检查 | `od.check()` | ❌ |
| 形式化推理 | `FormalPipeline().run(text)` | ⚠️ Phase1建议LLM,Phase3零LLM |
| 洞察推导 | `od.analyze()` | ✅ |
| 质量评分 | `InsightEngine.judge_quality()` | ✅ |
| 工具推荐 | `ToolForge().select()` | ❌ keyword ✅ LLM |

---

## 标准操作：分析项目

```python
from engine.derive import OntoDerive
od = OntoDerive("project-path")
s = od.derive()
for c in s.get("derived_conclusions",[]):
    print(f"[{c['type']}] {c['conclusion']}")
results = od.check()
```

## 形式化推理：从原始文本到结论

```python
from engine.pipeline_v4 import FormalPipeline
r = FormalPipeline().run("原始研究文本...")
# r["conclusions"] → 形式结论(确定/推测/不确定)
# r["report"] → 自然语言报告
for c in r["conclusions"]:
    print(f"[{c.certainty}] {c.conclusion}")
```

---

## 可用工具列表

### MCP (11工具)
`init derive check rounds generate analyze config delta` `toolforge_match select guide`

### Python API
`OntoDerive.derive()/check()/analyze()` `FormalPipeline().run()` `RuleReasoner.derive()` `FormalReasoner.reason()`

### CLI
`python3 engine/cli.py {init|derive|check|rounds|generate|toolforge} --project PATH`
