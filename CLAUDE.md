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

## 架构速览 (物理五层)

```
engine/
├── core/           核心引擎    derive/check/check_theory/pipeline
├── reasoners/      推理引擎    reasoner/reasoner_formal/reasoning/unified_reasoner
├── theories/       六论模块    bayesian/metrics/controller/logic/turing_k/ontolang
├── intelligence/   LLM智能     llm/insight/judge/prompts/got/react
├── foundation/     基础设施    typesystem/models/constants/utils/config/protocols
├── toolforge/      工具匹配    TF-IDF+keyword+hybrid (73工具)
├── ecosystem/      生态适配    Minerva/Sophia/Agora/eCOS
├── ontolang/       形式语言    递归下降解析器+AST
├── formalize.py    符号化引擎  LLM提取+规则降级+ABox/TBox构建
├── pipeline_v4.py  四阶段管线  文本→推理报告输出
├── cli.py          CLI入口     9子命令
├── mcp_server.py   MCP入口     11工具
├── extractor.py    文本提取器  上下文提取
└── watcher.py      文件监听    自动重推导
```
