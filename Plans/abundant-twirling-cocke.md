# OntoDerive v3.3 → v3.4 推理体系升级计划

> 基于SystemsThinking四层分析(Iceberg→CausalLoop→FindLeverage)
> 核心洞察: 正则匹配到LLM调用之间的能力断层是A2-A5所有问题的根因

## Context

三轮白盒对比揭示: 确定性规则(R1-R18)持续增强，LLM分析模式(A2-A5)长期停滞。根因是缺少语义中间层——从正则直接跳到LLM，中间没有TF-IDF/嵌入向量/轻量分类器。

## 执行计划

### P1: 止血+信息流 (2h) — LP6 + LP12

**1a. R19循环bug** (~40行)
- `reasoner.py._relation_reasoning`: 传递性推理加visited集合防循环
- 当前bug: `A→depends_on→B→depends_on→A` 输出 `A depends_on A`

**1b. 推理链路可解释性** (~50行)
- 每个derived_conclusion加`derivation_trail`字段
- 格式: `"R9: D-F1→D-F2→INF-L1"` 标注使用的规则+依赖链
- RuleReasoner.derive()中为每个结果追加trail

### P2: 统一+中间层 (3h) — LP10 + LP8

**2a. AnalyticsEngine纳入UnifiedReasoner** (~80行)
- AnalyticEngine.run()返回值封装为UnifiedConclusion
- certainty="probable", source="analytics"
- unified_reasoner.py扩展accept_analytics参数

**2b. 语义中间层 SemanticMatcher** (~160行)
- 新建 `engine/intelligence/semantic.py`
- TF-IDF + 余弦相似度做实体名模糊匹配
- 替换A2的精确字符串匹配 + A4的共享资源计数
- 给AnalyticsEngine注入matcher

### P3: 目标+声明式 (4h) — LP3 + LP4

**3a. A1过剩检测 + A5量化增强** (~100行)
- A1: 利用率<60%+库存>2x → 过剩信号
- A5: 问题数÷人数÷时间窗口 = 可行性比率

**3b. 规则YAML化 MVP** (~200行)
- `engine/foundation/rule_loader.py` — RuleLoader从YAML加载规则
- 3-5个示例规则YAML文件

### P4: 范式升级 (持续) — LP2

**4a. 连续推理谱系**
- `requires_llm: bool` → `semantic_depth: 0-5`
- 预算约束下自动选择推理深度

## 验证

- 162+ tests passed
- S5自循环: 不再输出 `A depends_on A`
- S1-S5回归: 分析模式输出质量不降
- 新增TF-IDF匹配测试
- 推理链路trail字段可读性验证
