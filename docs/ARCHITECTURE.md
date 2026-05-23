# OntoDerive v3.6.4 — 功能架构详解

> 知识工程分析平台。**747+ 测试**, 0 ruff 错误, 5层架构, 70+模块。
> 三模式：结构分析(无LLM) | 规则推理(无LLM) | 形式推理(需LLM Phase1)

---

## 一、设计哲学

**核心命题**：知识工程的本质是将"模糊洞见"转化为"可追溯、可验证、可复用的结构化知识"。

**四条设计原则**：

1. **事实先于推论** — 没有编号引用的断言不可信。每个方案断言必须可追溯到具体事实(D-Fx/P-Fx)
2. **双向闭环** — 正向推导(事实→推论→方案) + 反向规约检查 = 完整的知识螺旋
3. **六论融合** — 贝叶斯/信息论/控制论/图灵机/逻辑/形式语言，协同工作的知识处理管道
4. **LLM优先+规则降级** — Phase1用LLM做语义提取，失败时自动降级到规则引擎，确保零LLM环境可用

---

## 二、三模式运行架构

```
┌──────────────────────────────────────────────────────┐
│  模式1: 结构分析 (零LLM)                              │
│  derive() → check() → 13规约 + 贝叶斯置信度 + KQI    │
├──────────────────────────────────────────────────────┤
│  模式2: 规则推理 (零LLM)                              │
│  RuleReasoner(21规则+YAML23) + FormalReasoner(4模式)        │
│  → UnifiedReasoner 统一输出 (certain/probable/...)   │
├──────────────────────────────────────────────────────┤
│  模式3: 形式推理 (需LLM Phase1)                       │
│  FormalPipeline: LLM提取 → 符号化 → 形式推理 → 解读  │
│  降级: LLM失败 → 规则引擎 (覆盖约15-20%)              │
└──────────────────────────────────────────────────────┘
```

---

## 三、五层引擎架构

```
engine/
├── core/           核心引擎    derive/check/check_theory/pipeline
├── reasoners/      推理引擎    RuleReasoner(21规则+YAML23)+FormalReasoner(4)
│                               +UnifiedReasoner+reasoning_rules+reasoner_utils(统一输出)
├── theories/       六论模块    bayesian/metrics/controller/logic/
│                               turing_k/ontolang/analytics_patterns/analytics_constants
├── intelligence/   LLM智能     llm/insight/judge/prompts/got/react/providers
├── foundation/     基础设施    typesystem/models/constants/utils/
│                               config/protocols
├── toolforge/      工具匹配    TF-IDF+keyword+hybrid (73工具)
├── watcher.py      文件监听    自动重推导
├── extractor.py    文本提取    从自然语言提取事实
├── cli.py          CLI入口     14子命令
├── mcp_server.py   MCP入口    17工具
├── mcp_handlers.py MCP处理    17工具+Web仪表盘
├── web_server.py   Web仪表盘   FastAPI + MCP/HTTP
├── formalize.py    符号化      LLM提取+规则降级
└── pipeline_v4.py  管线        四阶段推理管线
```

---

## 四、MOF四层架构

```
M3 元元模型层 (OntoLang形式语言)
  │  实现：engine/theories/ontolang/ — 递归下降解析器 + AST
  │
M2 元模型层 (10元类型)
  │  实现：engine/foundation/typesystem.py — TypeValidator
  │
M1 领域模型层 (具体项目知识)
  │  实现：entities/ + facts/ 目录的Markdown表格
  │
M0 实例数据层 (不可辩驳的事实)
  │  实现：facts/data.md + facts/policy.md
```

---

## 五、核心模块详解

### 5.1 推导引擎 (engine/core/derive.py)

```
OntoDerive 类
├── derive()        结构分析 → derived_conclusions + derivation_hints
├── analyze()       LLM增强分析 → llm_insights
├── derive_formal() 形式推理入口 → 四阶段管线
├── check()         规约检查 → 13条规约
└── run_rounds(n)   多轮迭代至收敛
```

### 5.2 推理引擎 (engine/reasoners/)

```
UnifiedReasoner — 统一推理入口
├── RuleReasoner (21模式)
│   ├── 确定性: numeric_comparison, modus_ponens, subsumption, ...
│   ├── 启发式: shared_premise, disjunctive_syllogism, ...
│   └── 结构性: coverage, redundancy_warning, temporal_sequence, ...
├── FormalReasoner (4模式)
│   ├── subsumption (包含推理)
│   ├── transitivity (传递推理)
│   ├── constraint (约束传播)
│   └── classification (实例归类)
├── reasoning_rules.py   23条推理函数(从reasoner.py提取)
├── reasoner_utils.py    5个纯工具函数
└── 输出: UnifiedConclusion (certainty + derives_from + confidence)
```

### 5.3 符号化引擎 (engine/formalize.py)

```
Formalizer — LLM主提取 + 规则降级
├── extract_from_text(text, mode)
│   ├── llm_first: LLM优先 → 规则降级 (默认)
│   ├── llm_only: 仅LLM (无降级)
│   └── rule_only: 仅规则 (零LLM, 覆盖15-20%)
├── _rule_extract() → 正则匹配数值+实体
├── _validate() → TypeValidator ID格式校验
├── _build_abox_tbox() → ABox断言箱 + TBox术语箱
└── to_markdown() → 符号化知识输出
```

### 5.4 四阶段管线 (engine/pipeline_v4.py)

```
FormalPipeline.run(text)
├── Phase1: LLM提取 (Formalizer, 分块处理)
├── Phase2: 符号化 (ABox/TBox构建)
├── Phase3: 形式推理 (FormalReasoner, 零LLM)
└── Phase4: LLM解读 (生成自然语言报告)
```

### 5.5 LLM智能层 (engine/intelligence/)

```
intelligence/
├── llm.py       LLM客户端 (ollama/local API/openai/anthropic)
├── insight.py   统一洞察引擎 (4标准类型 + 缓存)
├── judge.py     LLM质量评估 (1-10分)
├── prompts.py   提示词模板 (4模板 + 4领域预设)
├── got.py       思维图谱 (Graph of Thoughts)
├── providers.py LLM Provider抽象(5后端+自动检测)
└── react.py     推理+行动 (7 Action原语)
```

### 5.6 工具匹配 (engine/toolforge/)

```
ToolForge (v2)
├── 三模式: keyword | tfidf | hybrid
├── 中文优化: bigram分词 + keyword默认模式
├── 73个思维工具 (6维度)
└── 输出: 推导指导 + 工具推荐
```

---

## 六、生态接口

```
┌──────────┐   研究结果    ┌──────────┐   范式推荐    ┌──────────┐
│ Minerva  │──────────────→│ OntoDerive│←──────────────│ Sophia   │
│ 深度研究  │  facts/生成   │  渊衍框架  │ 工具匹配推荐  │ 范式引擎  │
└──────────┘              └─────┬──────┘              └──────────┘
                               │
                          MCP路由层
                               │
                    ┌──────────┴──────────┐
                    │                     │
               ┌────┴─────┐         ┌─────┴────┐
               │  Agora   │         │   eCOS   │
               │ MCP路由  │         │ Agent编排│
               └──────────┘         └──────────┘
```

---

## 七、数据流全景

```
用户输入
  │
  ├── 模式1: 结构分析 (零LLM)
  │   ├── derive() → 扫描facts/entities/inferences/scheme
  │   │   ├── 贝叶斯置信度分布 (DAG sum-product)
  │   │   └── 逻辑蕴含图链深度 → derive-summary.json
  │   ├── check() → C-01~C-13 规约检查
  │   │   ├── C-09→C-10: 内存传递贝叶斯分布, 不重复实例化
  │   │   └── → check-result-{ts}.json
  │   └── analyze() → LLM增强洞察 (可选)
  │
  ├── 模式2: 形式推理 (LLM Phase1)
  │   ├── Phase1: LLM提取 (formalize.py, 分块2500字)
  │   │   └── 失败→规则引擎降级 (覆盖15-20%)
  │   ├── Phase2: 符号化 (ABox/TBox构建)
  │   ├── Phase3: 形式推理 (reasoner_formal.py, 零LLM)
  │   └── Phase4: LLM解读 → 自然语言报告
  │
  └── 迭代: 修改事实/推论 → re-derive → re-check → 收敛
```

**完整运行**: 结构分析约1秒, 形式推理取决于LLM响应时间。
