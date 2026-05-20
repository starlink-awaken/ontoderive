# Agent可读操作手册 v3.5

> AI Agent加载此项目时的标准操作流程。197 tests, 9分析模式, 5格式导出。

---

## Agent能力清单

| 操作 | 命令/代码 | 需要LLM吗 |
|------|----------|---------|
| 结构分析 | `od.derive()` | ❌ |
| 推导结论+trail | `summary["derived_conclusions"]` | ❌ |
| 规约检查 | `od.check()` | ❌ |
| 分析模式 (A1-A9) | 自动触发 (derive内置) | ❌ L0-L1, ⚠️ L4 |
| 关系推理 (R19) | 自动触发 (传递性+逆关系) | ❌ |
| 形式化推理 | `FormalPipeline().run(text)` | ⚠️ Phase1建议LLM |
| HTML/JSON导出 | `to_html(r)` / `--export html` | ❌ |
| 本体映射导出 | `--export jsonld\|turtle` | ❌ |
| 洞察推导 | `od.analyze()` | ✅ |
| 质量评分 | `InsightEngine.judge_quality()` | ✅ |
| 工具推荐 | `ToolForge().select()` | ❌ keyword ✅ LLM |

---

## 标准操作：分析项目

```python
from engine.derive import OntoDerive
od = OntoDerive("project-path")
s = od.derive()
# s["derived_conclusions"] → 含 trail/source/confidence
# s["derivation_hints"] → 结构提示
for c in s.get("derived_conclusions",[]):
    print(f"[{c.get('source','?')}|{c.get('derivation_trail','?')}] {c['conclusion'][:120]} ({c.get('confidence',0):.0%})")

# HTML导出
from engine.core.export import to_html
Path("report.html").write_text(to_html(s, "project-name"))
```

## 分析模式 (9种, 零LLM可用)

```python
from engine.theories.analytics import AnalyticsEngine
ae = AnalyticsEngine()
# A1供给弹性 A2风险传导 A3代理问题 A4激励相容 A5补救规划
# A6市场结构 A7博弈均衡 A8策略空间 A9信息生态
results = ae.run(facts, entities, inferences, relations, max_depth=0)
```
```

---

## 可用工具列表

### MCP (11工具)
`init derive check rounds generate analyze config delta` `toolforge_match select guide`

### Python API
`OntoDerive.derive()/check()/analyze()` `FormalPipeline().run()` `RuleReasoner.derive()` `FormalReasoner.reason()`

### CLI
`python3 engine/cli.py {init|derive|check|rounds|generate|toolforge} --project PATH`
