# OntoDerive — 渊衍框架 v3.1

> 知识工程分析平台。双模式：结构分析(无LLM) + 洞察推导(需LLM)

---

## Agent 标准操作流程

### 1. 快速了解项目

```bash
python3 engine/derive.py --project examples/z-park --derive --check
# 输出: 8事实, 推导结论10条, 规约检查13/13
```

### 2. 分析任意项目

```bash
# 结构分析 (无需LLM, 始终可用)
python3 engine/cli.py derive --project <path>

# 完整分析 (需要LLM, 输出洞察+评分)
ONTODERIVE_LLM_BACKEND=local python3 engine/cli.py analyze --project <path>
```

### 3. 推理规则 (8种推理 + 13种结构检查)

```python
from engine.derive import OntoDerive
od = OntoDerive("my-project")
summary = od.derive()
# summary["derived_conclusions"] → 推理结论列表
# summary["derivation_hints"]    → 结构提示列表
```

---

## 当前状态 (v3.1.1)

| 指标 | 数值 |
|------|------|
| 引擎模块 | 20+5子包 (5层架构) |
| 测试数 | 156, 全部通过 |
| 推理模式 | 8推理规则 + 13结构检查 |
| LLM后端 | ollama/local API/openai/anthropic |
| MCP工具 | 11个 |

---

## 架构速览

```
engine/
├── core/          核心引擎    derive/check/check_theory/pipeline
├── reasoners/     推理引擎    reasoner(21模式)/reasoning(选择器)
├── theories/      六论模块    bayesian/metrics/controller/logic/turing_k/ontolang
├── intelligence/  LLM智能     llm/insight/judge/prompts/got/react
├── foundation/    基础设施    typesystem/models/constants/utils/config/protocols
├── toolforge/     工具匹配    TF-IDF+keyword+hybrid (73工具)
├── ecosystem/     生态适配    Minerva/Sophia/Agora/eCOS
└── mcp_server.py  MCP入口    11工具
```
