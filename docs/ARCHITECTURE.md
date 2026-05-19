# OntoDerive v2.2 — 功能架构详解

> 事实驱动的一体化知识工程与方案推导框架

---

## 一、设计哲学

**核心命题**：知识工程的本质是将"模糊洞见"转化为"可追溯、可验证、可复用的结构化知识"，不是做一次分析，而是建立一套可迭代收敛的知识体系。

**三条设计原则**：

1. **事实先于推论** — 没有编号引用的断言不可信。每个方案断言必须可追溯到具体事实(D-Fx/P-Fx)
2. **双向闭环** — 正向推导(事实→推论→方案) + 反向规约检查(方案是否正确引用事实) = 完整的知识螺旋
3. **六论融合** — 贝叶斯/信息论/控制论/图灵机/逻辑/形式语言，不是并列的理论装饰，而是协同工作的知识处理管道

---

## 二、MOF四层架构

```
M3 元元模型层 (OntoLang形式语言)
  │  定义：什么是合法的实体/事实/推论/规约声明
  │  实现：engine/ontolang/ — 递归下降解析器 + AST + 语义分析
  │
M2 元模型层 (10元类型)
  │  定义：DOMAIN/FACT/INFERENCE/STATE/DOCUMENT/CONSTRAINT/PROCESSOR
  │  实现：engine/typesystem.py — TypeValidator + 前缀→类型映射
  │
M1 领域模型层 (具体项目知识)
  │  定义：这个项目的ORG/ROL/PRJ是什么，事实是什么
  │  实现：entities/目录 + facts/目录的Markdown表格
  │
M0 实例数据层 (不可辩驳的事实)
  │  定义：D-F1=240家企业, P-F9=京教科人办发[2026]2号
  │  实现：facts/data.md + facts/policy.md
```

**向上规约**（M0→M1→M2→M3）：从具体方案中抽象出可复用的模式→编写新规约→扩展形式语言
**向下推导**（M3→M2→M1→M0）：从元模型约束→领域建模→事实采集→方案生成

---

## 三、六论数据管道

```
          ┌─────────────┐
  输入 →  │  ToolForge   │  工具匹配：53种思维框架推荐
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  OntoLang   │  形式语言：解析实体/事实/推论声明
          │   Parser    │  → AST → 类型校验
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  Bayesian   │  贝叶斯层：DAG信念传播
          │   Layer     │  置信度从事实沿derives_from链传播
          │             │  输出：每个推论的概率 P(INF | premises)
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  Metrics    │  信息论层：KQI知识质量指数
          │   Layer     │  H(KB)熵 + 覆盖率 + 推导密度
          │             │  输入：贝叶斯置信度分布
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │ Controller  │  控制论层：PID反馈
          │   (PID)     │  P=当前违规 I=加权历史 D=变化率
          │             │  收敛检测 + 行动建议
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  Logic      │  逻辑层：蕴含图分析
          │   Graph     │  环检测 + 链深度 + 瓶颈节点
          └──────┬──────┘
                 ▼
          ┌─────────────┐
          │  Turing-K   │  图灵机层：知识状态机
          │             │  快照 → Delta → 停机检测
          └─────────────┘
```

---

## 四、模块详解

### 4.1 核心引擎 (derive.py + check.py)

```
OntoDerive 类 (147行)
├── derive()       正向推导：扫描facts/entities/inferences/scheme
│                   输出：derive-summary.json (含置信度分布+链深度)
├── check()        规约检查 → 委托给 check.py 的 run_check()
│                   输出：check-result-{timestamp}.json (13条规约)
├── run_rounds(n)  多轮迭代：derive → check → 重复至收敛
├── generate_report() 生成Markdown报告
└── resolve()      自动修复：创建缺失目录

check.py (270行) — 独立规约检查引擎
├── C-01~C-03  文件存在性 (浅层检查)
├── C-04~C-06  追溯/可证伪 (正则+启发式，含file:line定位)
├── C-07       实体ID合规 (TypeValidator集成)
├── C-08       引擎自检
├── C-09~C-10  贝叶斯/KQI (六论核心，预计算数据传递)
├── C-11~C-13  PID/图灵机/OntoLang
```

**关键设计**：C-09的贝叶斯结果通过内存变量 `_bayes_distribution` 直接传递给C-10，不再重复实例化BayesianLayer。

### 4.2 类型系统 (typesystem.py)

```
7种元类型定义：
  DOMAIN   → 领域实体 (ORG-/ROL-/PRJ-/RES-)
  FACT     → 事实数据 (D-F数字 / P-F数字)
  INFERENCE → 推论 (INF-/INF-V2-)
  STATE    → 状态标记 (T/F/H)
  DOCUMENT → 文档 (DOC-/CH-/SEC-/DCH-)
  CONSTRAINT → 约束 (CON-/IP)
  PROCESSOR → 引擎 (ENG-)

TypeValidator
├── check_id(id, declared_type) → TypeCheckResult
│     校验：前缀→类型映射 + 子类型合法性
├── check_batch(items) → 批量校验
└── summary() → 统计报告
```

### 4.3 贝叶斯层 (bayesian.py)

```
BayesianNetwork (DAG)
├── add_fact / add_inference → 构建节点
├── finalize() → 解析前向引用
├── detect_cycles() → DFS三色环检测
├── propagate() → 拓扑排序 + sum-product信念传播
└── to_dot() → Graphviz DOT可视化

BayesianLayer
├── scan_facts / scan_inferences → 从目录提取
├── build_network → 构建DAG
├── propagate_all → 主流程 (DAG→传播→回退)
├── get_distribution() → 公开接口：返回置信度分布
└── confidence_report() → 生成报告
```

### 4.4 信息论层 (metrics.py)

```
MetricsLayer
├── compute_kqi(precomputed_confs=None)
│     KQI = 0.25*熵项 + 0.25*追溯率 + 0.20*推导密度 + 0.15*实体 + 0.15*方案
├── get_kqi_trend() → 线性回归斜率 → improving/stable/declining
├── suggest_next_fact() → 基于KQI缺口建议改善方向
└── full_report() → 生成KQI报告
```

### 4.5 控制论层 (controller.py)

```
PIDController(kp=1.0, ki=0.5, kd=0.5, window=5, epsilon=0.1)
├── analyze() → PID信号 + 收敛检测 + 行动建议
│     P: 当前违规数
│     I: 指数衰减加权历史平均 (decay=0.85)
│     D: 滑动窗口平均变化率
├── _check_convergence() → |D均值| < epsilon
└── _generate_actions() → 具体修复建议
```

### 4.6 逻辑层 (logic.py)

```
EntailmentGraph
├── add_node / add_edge → 构建蕴含图
├── detect_cycles() → 共享utils.detect_cycles
├── chain_depths() → 最长/最短/平均推导链深度
├── bottlenecks() → 出度前5节点
├── redundant_paths() → 冗余推导路径
└── to_graphml() → GraphML导出
```

### 4.7 形式语言层 (ontolang/)

```
ontolang/
├── ast.py       AST节点定义 (EntityDef/FactDef/InferenceDef/ProtocolDef)
├── parser.py    手写递归下降解析器 (Lexer + Parser)
├── semantic.py  语义分析器 (前缀校验 + 引用有效性 + 重复检测)
├── codegen.py   代码生成 (AST↔Markdown↔JSON)
└── __init__.py  统一入口 (OntoLangParser v1兼容 + OntoLangParserV2)
```

### 4.8 管道编排 (pipeline.py)

```
DerivePipeline
├── stages = [ToolForgeStage, LoadStage, DeriveStage, CheckStage, ResolveStage, ReportStage]
├── set_goal(goal, context) → 设置分析目标
├── run(stages=None) → 执行指定阶段
├── to_analysis_result() → 输出统一AnalysisResult
└── to_dict() → 序列化
```

### 4.9 工具匹配 (toolforge/matcher.py)

```
ToolForge (v2)
├── 三模式匹配：
│     keyword: kw in search_text (快速，中文友好)
│     tfidf:  余弦相似度 (精确，需要英文/混合语料)
│     hybrid: 0.7*tfidf + 0.3*keyword (综合)
├── select(goal, context, top_n, mode)
├── match(goal, context) → 按6类别分组
└── to_inference_guide(goal, context) → 生成推导指导
```

---

## 五、生态接口

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

## 六、数据流全景

```
用户输入 (项目目录)
  │
  ├── derive() ──→ 扫描facts/entities/inferences/scheme
  │                ├── 贝叶斯置信度分布
  │                └── 逻辑蕴含图链深度
  │                └──→ derive-summary.json
  │
  ├── check() ──→ C-01~C-13 规约检查
  │              ├── C-09: BayesianLayer.get_distribution()
  │              ├── C-10: MetricsLayer.compute_kqi(precomputed_confs=↑)
  │              ├── C-11: PIDController.analyze()
  │              ├── C-12: KnowledgeTM.snapshot()
  │              ├── C-13: OntoLangParser.test_suite()
  │              └──→ check-result-{ts}.json
  │
  └── refine (人工/AI)
       └── 修改 facts/entities/inferences/scheme
            └── 重新 derive → check → 收敛
```

**关键**：C-09→C-10通过内存变量直接传递，不重复实例化。完整运行一次 `analyze`（含ToolForge+derive+check）约1秒。
