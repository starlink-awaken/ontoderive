# OntoDerive v3.3 推理体系 — 系统思维分析与迭代路线

> 基于 SystemsThinking 三个工作流：Iceberg (四层下潜) + CausalLoop (反馈环映射) + FindLeverage (Meadows 12杠杆点排序)

---

## 🧊 Iceberg 分析：从事件到心智模型

### Layer 1 — EVENTS (可见事件)

| 事件 | 状态 |
|------|------|
| R1-R18 规则推理 (21模式) | 100%可用, 零LLM, 162测试全部通过 |
| R9 本体归类增强版 | 100%正确, 前缀匹配bug已修复 |
| R19 关系推理 | 传递性+逆关系可用, 但存在循环引用bug |
| A1 供给弹性 | 确定性可用, 但缺少过剩检测(仅检测紧张) |
| A2 风险传导 | 依赖实体名精确匹配(depends_on链解析弱) |
| A3 代理问题 | 框架检测OK, 分析必须LLM |
| A4 激励不相容 | 语义匹配弱(仅检测共享资源, 无目标对比) |
| A5 补救规划 | 框架OK, 量化分析(时间/成本)待加强 |
| 属性约束+本体映射 | 成熟可用 |
| UnifiedReasoner | 已实现但仅合并RuleReasoner+FormalReasoner, AnalyticsEngine未纳入 |

### Layer 2 — PATTERNS (反复出现的模式)

**Pattern A: 确定性/LLM双速发展**
- 确定性规则(R1-R18)持续增强，每次迭代都加新规则
- LLM依赖的分析模式(A2-A5)长期停滞，`requires_llm=True`成为"先放着"的标签
- 模式形状：两个引擎的成熟度差距在扩大，不是缩小

**Pattern B: 分析模式的"检测-分析"裂缝**
- 每个AnalyticsPattern都有一个`detect`(确定性, 弱)和一个`analyze`(部分确定性+部分LLM)
- detect负责门控(触发与否)，analyze负责深度
- 裂缝在于：detect通过后，analyze的确定性部分太薄，LLM部分又太重
- A4最典型：detect仅检查"实体数>=3且关系>=2"，analyze完全依赖LLM

**Pattern C: 三引擎并行但分治**
- RuleReasoner(21规则, 约1000行) + FormalReasoner(4规则, 约140行) + AnalyticsEngine(5模式, 约370行)
- 三者输出格式不同、分类体系不同、集成方式不同
- UnifiedReasoner做了第一步合并，但AnalyticsEngine仍独立运行
- Pattern是"加新能力时总是加新引擎，而不是扩展现有引擎"

**Pattern D: 版本漂移的周期性复发**
- 之前的P0-P4计划专门修复了版本号漂移问题
- 根本原因是文档分散(README/ARCHITECTURE/ROADMAP/CLAUDE.md/changelog)且各自手动维护
- 当前已修复，但如果没有结构性防护(单一真相源)，6个月后会再次漂移

### Layer 3 — STRUCTURES (生成模式的结构)

**结构1: 双轨架构的激励不对称**
```
确定性推理路径: 事实/推论 → RuleReasoner → derived_conclusions (确定/概率/结构)
LLM增强路径:   事实/推论 → AnalyticsEngine → LLM → derived_conclusions (分析洞察)
```
- 确定性路径：开发成本低(写正则/逻辑)，测试容易(快照对比)，立即可用
- LLM路径：开发成本高(需要提示工程)，测试困难(非确定性输出)，依赖外部服务
- 结构性的激励：开发者自然倾向于确定性规则，LLM分析模式被推迟

**结构2: 语义鸿沟的单点桥接**
```
关键词匹配 ───[语义鸿沟]─── 真正的语义理解
   ↑                            ↑
   R1-R18的极限              A3-A5的需求
   (正则/前缀/字符重叠)       (需要LLM)
```
- 当前没有中间层：从正则匹配直接跳到LLM调用
- 缺少的层：TF-IDF相似度、嵌入向量检索、轻量分类器
- A2("依赖实体名")的根本原因：`_find_entity_for_fact`仅做精确字符串匹配(`info.get("name", "") in desc`)

**结构3: 规则系统的封闭性**
- 21个规则(R1-R18+R19-R21)全部硬编码在RuleReasoner的方法中
- 添加新规则=修改reasoner.py源码+写测试+跑全量回归
- 没有规则描述语言(DSL)，没有规则注册机制，没有插件系统
- 这是一个**不具自组织能力**的结构(对照Meadows LP 4)

**结构4: 分析模式与推理规则的边界模糊**
- R19(关系推理)做的是AnalyticsEngine该做的事(传递性推理需要领域知识)
- A1(供给弹性)做的部分事情RuleReasoner可以做(数值比较+阈值检测)
- 边界模糊导致：同一个洞察可能来自两个引擎，也可能两个引擎都漏掉

### Layer 4 — MENTAL MODELS (使结构感觉自然的心智模型)

**心智模型1: "确定性是好的, LLM是最后手段"**
- 体现在: requires_llm=False的规则有21个, requires_llm=True的只有3个
- 这个信念使确定性规则快速膨胀，LLM增强的分析模式停滞
- 它假设"确定性=可靠, LLM=不可靠"，但很多领域洞察(代理问题、激励不相容)本质上是语义问题，确定性方法覆盖面天然受限

**心智模型2: "分析模式是可复用的模板"**
- 体现在AnalyticsPattern的dataclass设计: name + description + detect + analyze
- 但实际模板是硬编码的Python函数，不是可配置的声明式模板
- 隐含假设：5个模式够用，新需求通过改代码满足
- 对照现实：博弈论/经济学/组织行为学有数十种分析框架

**心智模型3: "规则引擎是检查器(Checker)，不是生成器(Generator)"**
- 体现在: 大部分规则输出的是"警告/检测/问题"而非"建议/方案/预测"
- R18约束传播是个例外("建议为N个断言标注事实引用")
- 这个信念限制了系统从"分析型"到"建议型"的进化

**心智模型4: "代码结构=概念结构"**
- 体现在: 三种推理能力对应三个类(RuleReasoner/FormalReasoner/AnalyticsEngine)
- 统一推理(UnifiedReasoner)是一个新类而非重构旧类
- 这个信念导致每次扩展都加新类而非演进旧类

---

## 🔄 Causal Loop 分析：关键反馈环

```
变量:
  - 确定性规则数量 (NumRules)
  - 测试覆盖率 (TestCoverage)
  - 系统可靠性 (Reliability)
  - 开发者信心 (DevConfidence)
  - LLM分析模式数量 (NumAnalytics)
  - 分析洞察质量 (InsightQuality)
  - LLM调用成本/延迟 (LLMCost)
  - 分析模式使用频率 (UsageFrequency)
  - 系统复杂度 (Complexity)
  - 维护负担 (MaintenanceBurden)
  - 规则间交互bug (InteractionBugs)

箭头:
  NumRules →(+) TestCoverage (更多规则→更多测试)
  TestCoverage →(+) Reliability (更少回归)
  Reliability →(+) DevConfidence (系统稳定增强信心)
  DevConfidence →(+) NumRules (信心驱动加更多规则) [延迟: 短]
  DevConfidence →(+) NumAnalytics (信心也驱动加强分析模式) [延迟: 长]

  NumRules →(+) Complexity (规则越多系统越复杂)
  Complexity →(+) InteractionBugs (复杂度产生交互bug, 如R19循环)
  InteractionBugs →(−) Reliability (bug降低可靠性)
  Complexity →(+) MaintenanceBurden (复杂度增加维护负担)
  MaintenanceBurden →(−) NumRules (维护负担抑制新规则添加) [延迟: 中]

  NumAnalytics →(+) InsightQuality (分析模式多→洞察质量升)
  InsightQuality →(+) UsageFrequency (洞察好用→使用增加)
  UsageFrequency →(+) LLMCost (使用增加→LLM调用增加)
  LLMCost →(−) UsageFrequency (成本/延迟抑制使用)
  LLMCost →(−) NumAnalytics (成本压力抑制新分析模式开发)

  NumAnalytics →(+) Complexity (分析模式也增加复杂度)
  Complexity →(+) MaintenanceBurden

循环:
  R1 "成功孕育成功": NumRules→TestCoverage→Reliability→DevConfidence→NumRules (加强)
    - 早期主导，驱动确定性规则快速膨胀
  B1 "复杂度刹车": NumRules→Complexity→InteractionBugs→Reliability→(−)DevConfidence→(−)NumRules (平衡)
    - 随着规则数增加逐渐占据主导
    - R19循环bug就是这个刹车在起作用
  R2 "LLM陷阱": NumAnalytics→InsightQuality→UsageFrequency→LLMCost→(−)UsageFrequency→(−)NumAnalytics? (矛盾)
    - 实际上LLMCost抑制Usage但不直接抑制NumAnalytics，而是通过降低开发优先级间接抑制
    - 这是个延迟很长的反馈环，解释了为什么A2-A5长期停滞
  B2 "分析模式增长上限": NumAnalytics→Complexity→MaintenanceBurden→(−)NumAnalytics (平衡)
    - AnalyticsEngine与RuleReasoner的复杂度叠加

当前主导演化方向: R1主导(规则侧), 但B1正在加强(R19循环bug是信号)
分析侧的R2正在悄悄消耗分析模式的生命力(A2-A5质量停滞)
```

---

## 🎯 Leverage Point 分析：按Meadows 12杠杆点排序

### 当前系统目标 (隐含)
```
系统实际优化的目标: "确定性推理的覆盖面与正确性"
证据: 21个确定性规则 vs 3个LLM依赖模式, 162个测试几乎全是确定性测试
```

### 期望行为
```
"确定性与语义分析协同增强, 覆盖从逻辑检查到领域洞察的完整推理谱系"
```

### 候选干预及其杠杆点

| # | 干预 | Meadows层级 | 可行性 | 有效杠杆 | 描述 |
|---|------|-----------|--------|--------|------|
| **I1** | 修复R19循环bug | LP 12 (参数) | H | L | 修补特定bug，必要但低杠杆 |
| **I2** | A1加过剩检测 | LP 12 (参数) | H | L | 补全A1的另一半逻辑 |
| **I3** | A2实体匹配升级为TF-IDF | LP 8 (平衡环强度) | H | **M** | 在正则匹配与LLM之间插入中间层 |
| **I4** | AnalyticsEngine输出纳入UnifiedReasoner | LP 10 (存流结构) | H | **M** | 统一三引擎输出格式, 消除分治 |
| **I5** | 推理链路可解释性(每结论标注推导路径) | LP 6 (信息流) | M | **H** | 让用户看见推理过程, 行为自校准 |
| **I6** | 规则声明式化(Rules-as-Data: YAML/JSON定义规则) | LP 4 (自组织) | M | **VH** | 规则可插拔, 新增不需改源码 |
| **I7** | 系统目标从"覆盖率"转向"可行动洞察数" | LP 3 (目标) | L (需重新定义成功) | **VH** | 改变度量→改变行为→改变输出 |
| **I8** | 范式: 从"确定性+LLM双轨"到"连续推理谱系" | LP 2 (范式) | L (最大阻力) | **最高** | 规则/统计/嵌入/LLM视为连续谱 |

---

## 📋 推荐迭代路线 (按有效杠杆排序)

### Phase 1: 止血+信息流 (本周, 约2h) — LP 6 + LP 12

**1a. 修复R19循环bug (LP 12, 必要但非高杠杆)**
- 位置: `reasoner.py._relation_reasoning`中的传递性推理使用简单BFS，缺少visited集合
- 修复: 在传递闭包计算中加入`visited`防止循环

**1b. 推理链路可解释性 (LP 6, 高杠杆)**
- 问题: 当前`derived_conclusions`输出只含结论文本+置信度，不显示推导路径
- 方案: 每个结论增加`derivation_trail`字段，标注"R9: D-F1→INF-A→INF-B"
- 这相当于Meadows的"把电表移到走廊"——用户看见推导路径后会自行校准对结论的信任度
- 改动量: ~50行, 在RuleReasoner.derive()中为每个结果追加trail字段

### Phase 2: 统一+中间层 (下周, 约3h) — LP 10 + LP 8

**2a. AnalyticsEngine输出纳入UnifiedReasoner (LP 10)**
- 问题: AnalyticsEngine独立运行, 输出格式与前两者不同
- 方案: AnalyticEngine.run()的返回值封装为UnifiedConclusion, certainty="probable", source="analytics"
- 改动量: ~80行, 包括analytics.py适配 + unified_reasoner.py扩展

**2b. 建立语义匹配中间层 (LP 8, 强平衡环)**
- 问题: `_find_entity_for_fact`仅做精确字符串匹配, `_detect_incentive_issue`仅做计数
- 方案: 
  - 添加`SemanticMatcher`类, 用TF-IDF+余弦相似度做实体名模糊匹配
  - 给AnalyticsEngine注入matcher, 替换当前的精确匹配
  - A2风险传导的实体匹配升级, A4激励不相容的共享资源检测升级
- 改动量: ~120行新类 + ~40行analytics.py修改

### Phase 3: 目标+自组织 (下下周, 约4h) — LP 3 + LP 4

**3a. 度量从"覆盖率"转向"可行动洞察" (LP 3)**
- 问题: 系统当前度量是事实覆盖率、推导链深度——这些是过程指标
- 方案:
  - 新增指标: 可行动洞察数(含"建议"/"方案"关键词的结论), 洞察采纳率
  - derive()输出增加`actionable_insights`字段
  - 每个AnalyticsPattern的analyze增加"行动建议"输出
- 改动量: ~150行(metrics.py + derive.py + analytics.py)

**3b. 规则声明式化 (LP 4, 自组织)**
- 问题: 21个规则硬编码, 新规则=改源码
- 方案:
  - 定义规则描述格式(YAML):
    ```yaml
    id: R22
    name: trend_detection
    category: analytics
    premises: ["has_timestamps", "numeric_change > 20%"]
    conclusion_template: "{entity}的{metric}在{period}内变化{change}%, 趋势{trend_direction}"
    confidence: 0.75
    ```
  - 实现RuleLoader从YAML加载规则
  - MVP阶段: 支持3-5个简单规则类型, 保留Python规则作为复杂规则的后备
- 改动量: ~200行(RuleLoader新类 + YAML schema + 3个示例规则)

### Phase 4: 范式升级 (持续, ~6h) — LP 2

**4a. 连续推理谱系 (LP 2, 范式)**
- 当前范式: "确定性(规则) vs 非确定性(LLM)" 二元对立
- 目标范式: 推理方法是一个连续谱:
  ```
  正则匹配 → TF-IDF → 嵌入向量 → 轻量分类器 → 小模型 → 大模型(LLM)
  (确定性递增)                                    (语义理解递增)
  ```
- 具体行动:
  - 将`requires_llm: bool`改为`semantic_depth: 0-5` (0=纯正则, 5=纯LLM)
  - 每个分析模式标注它在谱系上的最佳位置
  - 预算约束下自动选择: 成本低时用LLM, 成本高时降级到嵌入/分类器
- 改动量: ~300行(新SemanticDepth枚举 + AnalyticsEngine选择逻辑 + 新模式定义)

---

## 总结：为什么按这个顺序

1. **Phase 1 (LP 6 + LP 12)**: 最低成本, 即时收益。R19修复是必要前提；推理可解释性(把电表移到走廊)改变使用者行为而不改变系统结构，是Meadows最推崇的"低成本高杠杆"干预。

2. **Phase 2 (LP 10 + LP 8)**: 中等成本, 结构收益。统一三引擎消除长期的分治成本；语义中间层填补正则到LLM之间的能力断层，这个断层是A2-A5所有问题的根源，补上它=一次性解决4个分析模式的底层瓶颈。

3. **Phase 3 (LP 3 + LP 4)**: 较高成本, 改变游戏规则。度量转向"可行动洞察"使整个系统目标对齐；规则声明式化赋予系统自组织能力(Meadows LP 4是"系统改变自身规则的能力")。

4. **Phase 4 (LP 2)**: 最高成本, 范式革命。连续推理谱系是对"确定性vsLLM"二元论的超越(Meadows LP 1的雏形)。它不是必须立即做的, 但Phase 1-3的成功会让Phase 4的必要性自然浮现。

**核心洞察**: 当前系统最大的瓶颈不是缺少LLM能力, 而是"正则匹配"到"LLM调用"之间存在一个巨大的能力断层。填补这个断层(Phase 2b的语义中间层)是撬动整个A系列分析模式升级的支点。一次建设, 四个模式(A2/A3/A4/A5)受益。
