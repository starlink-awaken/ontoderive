# Agent可读的操作手册

> 当AI Agent（Claude Code/Gemini CLI/Codex）被加载到此项目时，按此文档操作。

---

## Agent能力清单

| 操作 | 命令/代码 | 需要LLM吗 |
|------|----------|---------|
| 结构分析 | `od.derive()` 或 CLI `derive` | ❌ 不需要 |
| 推导结论 | `summary["derived_conclusions"]` | ❌ 不需要 |
| 规约检查 | `od.check()` 或 CLI `check` | ❌ 不需要 |
| 洞察推导 | `od.analyze()` 或 CLI `analyze` | ✅ 需要 |
| 质量评分 | `judge_project()` | ✅ 需要 |
| 工具推荐 | `ToolForge().select()` | ❌ keyword/TF-IDF ✅ LLM语义 |
| 矛盾检测 | `RuleReasoner().derive()` | ❌ 词对 ✅ LLM语义 |

---

## 标准操作：分析一个项目

```python
from engine.derive import OntoDerive
import json

# 步骤1: 结构分析
od = OntoDerive("project-path")
summary = od.derive()

# 步骤2: 读取推导结论
for c in summary.get("derived_conclusions", []):
    print(f"[{c['type']}] {c['conclusion']} (置信度:{c['confidence']})")

# 步骤3: 规约检查
results = od.check()
passed = sum(1 for r in results if r["passed"])
print(f"规约: {passed}/{len(results)} 通过")

# 步骤4 (可选, 需要LLM): 深度洞察
if od._try_llm():
    full = od.analyze()
    for insight in full.get("llm_insights", []):
        print(f"[{insight['type']}] {insight['content']}")
```

---

## 创建分析项目

```bash
python3 engine/cli.py init my-analysis
# 编辑 my-analysis/facts/data.md (数据事实)
# 编辑 my-analysis/inferences/analysis.md (推论)
# 编辑 my-analysis/scheme/report.md (方案)
python3 engine/cli.py derive --project my-analysis
python3 engine/cli.py check --project my-analysis
```

---

## 事实格式规范

```
| 编号 | 数据 | 数值 | 来源 |
| D-F1 | 日活用户 | 500万 | 运营后台 |
| D-F2 | 月营收 | 2.3亿 | 财务报表 |
```

## 推论格式规范

```
## INF-L1：推论标题
推导过程: ...
结论: ...
- derives_from: [D-F1, D-F2]
confidence: high|inference|medium|low
```

---

## 可用工具列表

### MCP (11工具)
`ontoderive_init` `derive` `check` `rounds` `generate` `analyze` `config` `delta`
`toolforge_match` `select` `guide`

### Python API
`OntoDerive.derive()/check()/analyze()` `RuleReasoner.derive()` `InsightEngine.judge_quality()`

### CLI
`python3 engine/cli.py {init|derive|check|rounds|generate|toolforge} --project PATH`
