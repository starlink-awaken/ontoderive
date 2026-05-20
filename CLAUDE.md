# OntoDerive v3.5 — 渊衍框架

> 知识工程分析平台。三模式+分析引擎+多格式导出。197 tests, 57模块, 8,600行。

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

## 当前状态 (v3.5.0)

| 指标 | 数值 |
|------|------|
| 引擎模块 | 57 (5层架构) |
| 测试数 | 197, 全部通过 |
| 推理规则 | 19条(R1-R19) + 23条YAML规则 |
| 分析模式 | 9个(A1-A9), semantic_depth 0-5 |
| 导出格式 | HTML/JSON/Markdown/JSON-LD/Turtle |
| LLM后端 | ollama/local API/openai/anthropic |

## 架构速览 (物理五层 + 能力矩阵)

```
engine/
├── core/           derive/check/check_theory/pipeline/export
├── reasoners/      reasoner/reasoner_formal/reasoning/unified_reasoner
├── theories/       bayesian/metrics/controller/logic/turing_k/ontolang/analytics
├── intelligence/   llm/insight/judge/prompts/got/react
├── foundation/     typesystem/models/constants/utils/config/protocols
│                   ontology_map/rule_loader/semantic/rules/
├── toolforge/      73工具 TF-IDF+keyword+hybrid
├── ontolang/       递归下降解析器+AST+语义分析+代码生成
├── formalize.py    LLM提取+规则降级+ABox/TBox+属性约束
├── pipeline_v4.py  四阶段: 提取→符号化→推理→解读
├── cli.py          9子命令 + --export html|json|jsonld|turtle
└── mcp_server.py   11工具 JSON-RPC

分析模式 (A1-A9): 供给弹性/风险传导/代理问题/激励相容/补救规划/市场结构/博弈均衡/策略空间/信息生态
推理谱系: L0(纯规则)→L1(TF-IDF)→L2(嵌入)→L3(分类器)→L4(小模型)→L5(LLM)
```
