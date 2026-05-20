# OntoDerive Changelog

## v3.5.0 (2026-05-20)

### 分析模式引擎
- A6 MarketStructure: HHI集中度+CR3+市场类型判定 + 15关键词检测
- A7 GameEquilibrium: 囚徒困境识别+零和博弈+协调博弈
- A8 StrategicOptions: 博弈树深度+帕累托前沿+策略空间枚举
- A9 InfoEcology: 信息生态健康度(虚假率×信任度×共识度)

### 规则系统
- YAML规则 4→23条 (R1-R19 + R22-R25 全声明式)
- RuleLoader: 自动加载全部*.yaml规则文件
- _TYPE_TO_RULE提升为类常量

### 引擎统一
- UnifiedReasoner成为derive唯一推理入口
- 四层分类: certain/probable/structural/analytical
- derivation_trail全链路可追溯

### 代码质量
- 版本号全局统一v3.5.0 (6处)
- SemanticMatcher去重 (intelligence/=re-export)
- Ruff 180→101 (39 fixed)
- _safe_get死代码清除
- 新模块197 tests

## v3.4.0 (2026-05-19-20)

### 推理体系升级
- R19循环修复: 传递性推理加visited防自循环
- 推理链路可解释性: derivation_trail字段 (R1: D-F1→D-F2)
- AnalyticsEngine纳入UnifiedReasoner (5层来源: rule/formal/analytics)

### 语义匹配
- SemanticMatcher: TF-IDF+余弦相似度, 零LLM零外部依赖
- A2/A4升级: 语义匹配替换精确字符串
- 依赖方向修复: SemanticMatcher移到foundation/

### 分析模式
- A1供给弹性: +过剩检测(利用率<60%)
- A5可行性比率: 问题数÷人数÷时间窗口→可行/紧张/不可行
- semantic_depth 0-5: 连续推理谱系

### 本体建模
- 属性约束校验: _validate_properties
- R9包含推理增强: 分类建议+新类型检测+误分类
- R19关系推理: 传递性+逆关系+域约束
- OntologyMapper: JSON-LD/Turtle导出
- OntoLang parser: 关系解析+词汇表

## v3.3.0 (2026-05-18-19)

### 架构收敛
- 五层物理拆分: core/reasoners/theories/intelligence/foundation
- 31模块迁移至子包 (git mv)
- 所有导入: engine.xxx.yyy绝对路径
- 版本号统一v3.3.0

### 知识提取
- formalize.py: LLM主提取+规则降级引擎
- 规则引擎: 16事实模式+8实体模式
- 实体提取: 精确模式+去重+连接词前缀清理

### 推理引擎
- RuleReasoner: 21种推理模式
- FormalReasoner: 包含/传递/约束/归类
- UnifiedReasoner: 三引擎统一输出
- 语义域过滤器: 数值比较噪声58%→<5%

### 生态集成
- ToolForge: TF-IDF+keyword+hybrid 73工具
- MCP Server: 11工具 JSON-RPC
- CLI: 9子命令 (含formal/watch/extract)
- 生态适配器: Minerva/Sophia/Agora/eCOS

## v3.2.0 (2026-05-17)

### 形式推理管线
- pipeline_v4: 四阶段 (LLM提取→符号化→形式推理→解读)
- 形式推理: 确定/推测/不确定三级
- LLM增强: 洞察引擎+质量评估+提示词模板

### 六论融合
- Bayesian: DAG信念传播 (sum-product)
- Metrics: KQI知识质量指数
- Controller: PID控制论收敛检测
- Logic: 蕴含图+矛盾检测
- Turing-K: 知识状态机快照
- OntoLang: 形式语言解析器

## v3.1.0 (2026-05-16)

### 核心引擎
- OntoDerive: 结构分析 + 规则推理引擎
- Check: 13条规约 C-01~C-13
- Pipeline: 多阶段管道编排
- 初始类型系统: 10元类型 + TypeValidator

### 基础能力
- 测试框架: pytest 162 tests
- 项目初始化: ontoderive init
- Markdown格式知识表示
