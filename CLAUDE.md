# OntoDerive v3.3 — 渊衍框架

> 知识工程分析平台。三模式：结构分析(无LLM) | 规则推理(无LLM) | 形式推理(需LLM Phase1)

---

## Agent 标准操作流程

### 1. 快速了解
```bash
python3 engine/cli.py derive --project examples/z-park --check
```

### 2. 结构分析 (无LLM)
```python
from engine.derive import OntoDerive
s = OntoDerive("my-project").derive()
# s["derived_conclusions"] → 推导结论列表
# s["derivation_hints"] → 结构提示列表
```

### 3. 形式化推理 (四阶段管线)
```python
from engine.pipeline_v4 import FormalPipeline
r = FormalPipeline().run("原始研究文本...")
# Phase1: LLM提取(降级规则引擎) → Phase2: 符号化 → Phase3: 形式推理 → Phase4: 解读
```

---

## 当前状态 (v3.3.0)

| 指标 | 数值 |
|------|------|
| 引擎模块 | 23+5子包 (5层架构) |
| 测试数 | 162, 全部通过 |
| 推理模式 | 8推理规则+13结构检查+4形式推理 |
| LLM后端 | ollama/local API/openai/anthropic |

## 架构速览

```
engine/
├── core/           核心引擎    derive/check/check_theory/pipeline
├── reasoners/      推理引擎    旧RuleReasoner(21模式)+新FormalReasoner(4模式)
├── theories/       六论模块    bayesian/metrics/controller/logic/turing_k/ontolang
├── intelligence/   LLM智能     llm/insight/judge/prompts/got/react
├── foundation/     基础设施    typesystem/models/constants/utils/config/protocols
├── toolforge/      工具匹配    TF-IDF+keyword+hybrid (73工具)
├── ecosystem/      生态适配    Minerva/Sophia/Agora/eCOS
├── formalize.py    符号化引擎  LLM提取+规则降级+ABox/TBox构建
├── reasoner_formal.py 形式推理 包含/传递/约束/归类(确定/推测/不确定)
├── pipeline_v4.py  四阶段管线  文本输入→推理报告输出
└── mcp_server.py   MCP入口    11工具
```
