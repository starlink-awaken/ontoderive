# Graph Report - .  (2026-05-18)

## Corpus Check
- Corpus is ~37,776 words - fits in a single context window. You may not need a graph.

## Summary
- 854 nodes · 1220 edges · 68 communities (62 shown, 6 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 202 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 66|Community 66]]

## God Nodes (most connected - your core abstractions)
1. `Parser` - 25 edges
2. `OntoDerive` - 23 edges
3. `Config` - 22 edges
4. `ToolForge` - 20 edges
5. `KnowledgeTM` - 19 edges
6. `DerivePipeline` - 19 edges
7. `BayesianLayer` - 19 edges
8. `MetricsLayer` - 18 edges
9. `PIDController` - 18 edges
10. `TypeValidator` - 18 edges

## Surprising Connections (you probably didn't know these)
- `test_rf_file_exists()` --calls--> `rf()`  [INFERRED]
  tests/test_utils.py → engine/utils.py
- `test_rf_file_not_exists()` --calls--> `rf()`  [INFERRED]
  tests/test_utils.py → engine/utils.py
- `test_wf_creates_parent()` --calls--> `wf()`  [INFERRED]
  tests/test_utils.py → engine/utils.py
- `test_all_md()` --calls--> `all_md()`  [INFERRED]
  tests/test_utils.py → engine/utils.py
- `test_all_md_empty()` --calls--> `all_md()`  [INFERRED]
  tests/test_utils.py → engine/utils.py

## Communities (68 total, 6 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (43): max, min, BayesianLayer, BayesianNetwork, OntoDerive 贝叶斯层 v2 — DAG信念传播 ===================================== 基于有向无环图的信念传播：, 公开方法：返回置信度分布供Pipeline/Metrics消费, 有向无环图：节点=事实+推论，边=derives_from, Sum-product信念传播 — 多轮迭代直至收敛 (+35 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (31): Config, _deep_merge(), _load_yaml(), OntoDerive 配置系统 ================== 支持 ontoderive.yaml 配置文件，合并链：defaults → projec, CheckStage, DerivePipeline, DeriveStage, LoadStage (+23 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (23): Enum, AST, EntityDef, FactDef, InferenceDef, NodeType, ParseError, ProtocolDef (+15 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (22): get_derivation_guide(), OntoDerive 生态适配器 — Sophia集成 ==================================== Sophia范式推荐 → To, 将Sophia范式推荐结果转为ToolForge匹配输入, 为Sophia提供框架推荐（实现ToolForgeInterface）, 为Sophia生成推导指导（实现ToolForgeInterface）, recommend_frameworks(), sophia_to_toolforge(), main() (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (25): CheckResult, DeriveSnapshot, Entity, Fact, Inference, OntoDerive 数据模型 =================== dataclass 定义所有核心类型，消除各模块中 ad-hoc dict。 所有引擎模, Scheme, KnowledgeTM (+17 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (18): AgoraAdapter, _import_derive(), _import_toolforge(), OntoDerive 生态适配器 — Agora MCP路由 ====================================== 将MCP调用映射到O, Agora MCP路由适配器 — 按工具名前缀路由到OntoDerive MCP, route(), create_observer(), ECOSObserver (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (12): OntoDerive 类型系统 — MOF十元类型校验 ====================================== 实现10元类型的定义和校验, TypeCheckResult, TypeValidator, test_batch_check(), test_has_errors(), test_invalid_prefix(), test_summary(), test_type_mismatch() (+4 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (8): PIDController, OntoDerive 控制论层 v2 — PID反馈 + 收敛检测 =============================================, 收敛判定: |D| < epsilon 且最近D值稳定, test_adaptive_thresholds(), test_analyze_empty(), test_analyze_returns_keys(), test_derivative_with_no_history(), test_integral_with_no_history()

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (13): confidence_distribution, count, mean, derived_at, entailment_graph, cycles, edges, max_depth (+5 more)

### Community 9 - "Community 9"
Cohesion: 0.32
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (5): build_from_project(), EntailmentGraph, OntoDerive 逻辑层 — 蕴含图分析 =============================== 构建知识库的有向图模型，支持： - 推导链分析（最, 蕴含图：节点=事实+推论，边=derives_from, 计算每个节点的推导链深度（从根事实出发的最长路径）

### Community 11 - "Community 11"
Cohesion: 0.14
Nodes (6): DeriveInterface, PipelineObservable, OntoDerive 生态接口协议 ======================= 定义 Minerva/Sophia/Agora/eCOS 可消费的正式接口契, Minerva/Sophia/eCOS 可消费的推导引擎接口, ToolForgeInterface, Protocol

### Community 12 - "Community 12"
Cohesion: 0.21
Nodes (7): file_count, state, entities, facts, inferences, scheme_files, timestamp

### Community 13 - "Community 13"
Cohesion: 0.24
Nodes (11): err(), handle_request(), respond(), test_initialize(), test_ontoderive_check(), test_ontoderive_config(), test_toolforge_guide(), test_toolforge_select() (+3 more)

### Community 14 - "Community 14"
Cohesion: 0.15
Nodes (12): categories, methodologies, patterns, principles, skills, strategies, theories, meta (+4 more)

### Community 15 - "Community 15"
Cohesion: 0.18
Nodes (10): CROSS_LAYER, DERIVATION_HEALTH, SCHEME_COMPLIANCE, SSOT_INTEGRITY, meta, categories, name, rule_count (+2 more)

### Community 16 - "Community 16"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 17 - "Community 17"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 19 - "Community 19"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 21 - "Community 21"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 22 - "Community 22"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 23 - "Community 23"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 29 - "Community 29"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 30 - "Community 30"
Cohesion: 0.27
Nodes (3): ContextExtractor, OntoDerive 上下文提取器 — 从本地文件/网页提取事实 ===============================================, 输出为OntoDerive facts/data.md格式

### Community 31 - "Community 31"
Cohesion: 0.2
Nodes (9): checked_at, details, passed, severities, BLOCKER, ERROR, PASS, WARN (+1 more)

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (7): author, name, description, keywords, mcpServers, name, version

### Community 36 - "Community 36"
Cohesion: 0.25
Nodes (7): PYTHONPATH, mcpServers, ontoderive, args, command, description, env

### Community 38 - "Community 38"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 39 - "Community 39"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 40 - "Community 40"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 41 - "Community 41"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 43 - "Community 43"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 44 - "Community 44"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 45 - "Community 45"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 47 - "Community 47"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 48 - "Community 48"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 49 - "Community 49"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 50 - "Community 50"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 51 - "Community 51"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 52 - "Community 52"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 53 - "Community 53"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 56 - "Community 56"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (6): entities, facts, file_count, inferences, scheme_files, timestamp

### Community 58 - "Community 58"
Cohesion: 0.33
Nodes (5): error, retry_count, timestamp, tool_input_preview, tool_name

### Community 59 - "Community 59"
Cohesion: 0.33
Nodes (5): agents, last_updated, total_completed, total_failed, total_spawned

## Knowledge Gaps
- **296 isolated node(s):** `PASS`, `WARN`, `ERROR`, `BLOCKER`, `timestamp` (+291 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OntoDerive` connect `Community 0` to `Community 1`, `Community 35`, `Community 4`, `Community 37`, `Community 5`, `Community 7`, `Community 30`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `ToolForge` connect `Community 3` to `Community 0`, `Community 1`, `Community 5`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `KnowledgeTM` connect `Community 4` to `Community 0`, `Community 13`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Parser` (e.g. with `OntoLangParserV2` and `OntoLangParser`) actually correct?**
  _`Parser` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `OntoDerive` (e.g. with `BayesianLayer` and `MetricsLayer`) actually correct?**
  _`OntoDerive` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Config` (e.g. with `ToolForgeStage` and `LoadStage`) actually correct?**
  _`Config` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ToolForge` (e.g. with `AgoraAdapter` and `tf()`) actually correct?**
  _`ToolForge` has 5 INFERRED edges - model-reasoned connections that need verification._