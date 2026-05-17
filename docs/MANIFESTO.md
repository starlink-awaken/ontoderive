# OntoDerive 渊衍纲领

> 版本 1.0 | 最后更新 2026-05-16
> 本文档是 OntoDerive 框架的元纲领。任何 AI agent 阅读本文档后，应能独立复现一套完整的事实驱动知识工程与方案推导体系。

---

## 一、核心信念

### 1.1 一条公理

**任何有价值的方案，都是从可验证的事实中推导出来的。**

如果方案中的断言不能追溯到具体的事实编号，这个断言就是猜测而非结论。如果方案中的关键判断没有附带"如果X月后Y没发生则重新评估"的条件，这个判断就是空话而非决策。

### 1.2 三条原则

1. **事实先于推论**：没有事实编号的推论不被采用。推论可以被新事实修正。
2. **可证伪**：每个关键判断必须附带退出条件。不可证伪的判断不是知识，是信仰。
3. **双向闭环**：正向推导（事实→方案）和反向校验（方案→规约→修复）必须完整。缺少任何一个方向的循环都是不完整的。

### 1.3 一条纪律

**不做一次性交付，做持续迭代的闭环。** 每一轮推导产生新的知识快照，快照之间的差异即"学到了什么"。同一份方案经过多轮迭代收敛，每轮缺口闭环率应持续提升。

---

## 二、架构概览

### 2.1 MOF四层

```
M3: 元元模型层 — "建模语言的定义语言"
    OntoLang BNF语法, 元类型构造子, 元关系矩阵
    ↓ 实例化
M2: 元模型层 — "建模语言"
    10元类型, 4元关系, 4元约束, 26种ID前缀
    ↓ 映射
M1: 模型层 — "领域概念化"
    TBox(术语箱: 概念+属性) + ABox(断言箱: 实例+关系)
    ↓ 实例化
M0: 实例/数据层 — "原始事实"
    D-Fx数据事实, P-Fx政策事实, 所有事实标注来源
```

### 2.2 六层能力

| 层 | 理论来源 | 当前实现 | 状态 |
|----|---------|---------|------|
| 本体核 | 形式本体论 | 10元类型+4元关系+元关系矩阵 | ✅ v1.2 |
| 形式语言 | 形式语言理论 | OntoLang DSL规划中 | 📋 |
| 逻辑层 | 一阶逻辑+模态逻辑 | INF推论+derives_from蕴含链 | ✅ v1.2 |
| 贝叶斯层 | 概率论+贝叶斯统计 | confidence: 2级(high/medium) | 📋 |
| 信息论层 | 香农信息论 | 无 | 📋 |
| 控制论层 | 维纳控制论 | 无 | 📋 |

### 2.3 核心推导链

```
ToolForge 前置 ──→ 事实基座(What is) → 本体模型(What exists)
  (工具匹配)          → 推论体系(What follows) → 方案文档(What to do)
                          ↑ 双向规约校验 ↓
                      (规约约束 + 违规检测 + 修复建议)
```

### 2.4 ToolForge 前置匹配 (v2.0)

推导的第一步是选择正确的分析框架。ToolForge（原 MindForge）在推导前自动匹配适合的思维工具：

```
用户目标 → ToolForge 匹配 → 52工具目录 → Top-N框架推荐
                                              ↓
                                    推导指导(inferences/_toolforge_guide.md)
                                              ↓
                                    约束后续的事实收集和推论方向
```

**联动方式**：
```bash
# 带工具匹配的推导
python3 engine/derive.py --project . --with-tools --goal "目标" --derive

# 独立工具匹配
python3 engine/toolforge/matcher.py "目标" --inference-guide

# MCP 服务
python3 engine/toolforge/mcp_server.py
```

---

## 三、实体系统

### 3.1 10元类型

| 元类型 | 本质 | 实体前缀 | 核心能力 |
|--------|------|---------|---------|
| DOMAIN | 现实世界中的"东西" | ORG-/ROL-/PRJ-/RES- | part_of, participates_in |
| FACT | 可验证的陈述 | DAT-/POL- | 被cites, 被derives_from |
| INFERENCE | 基于事实的推导 | INF-/IP- | derives_from, maps_to |
| RELATION | 连接实体的边 | 无独立ID | 无 |
| STATE | 系统行为节点 | T-/F-/H- | transitions_to, interlocks_with |
| DOCUMENT | 知识组织形态 | DOC-/CH-/SEC- | contains, maps_to |
| CONSTRAINT | 质量门禁 | CON- | 被satisfies |
| PROCESSOR | 计算过程 | ENG- | processes, generates |
| PROBABILISTIC | 概率分布 | BAY-/PRIOR-/POST- | belief_update(待实现) |
| METRIC | 可量化指标 | KQI-/MEAS- | measure, compare(待实现) |

### 3.2 命名空间

```
od:{domain}:{type}-{name}@{version}

domain: 项目/领域标识 (如 guozhuan, analysis, meta)
type: 实体类型前缀 (如 ORG, INF, D-F)
name: 实体名称 (如 国转中心, L1)
version: 可选, 默认latest
```

### 3.3 事实编号体系

```
D-F{数字}: 数据事实(有数值+来源+时间戳)
P-F{数字}: 政策事实(有文号+发布主体+日期)

每个事实必须标注:
- 来源: 可追溯的原文出处
- 时间: 采集时间
- 可信度: fact(高) / estimate(中) / assumption(低)
```

---

## 四、推导引擎

### 4.1 核心流程

```python
# 6个核心命令:
init:     创建项目骨架(facts/entities/inferences/scheme)
derive:   扫描事实/实体/推论 → 生成推导摘要
check:    执行8条规约 → 输出通过/失败/修复建议
resolve:  自动修复可修复项(如缺失目录)
rounds:   多轮迭代(derive→check→report→fix→再derive)
generate: 生成markdown推导报告
```

### 4.2 8条规约

| 编号 | 检查项 | 严重度 | 触发条件 | 修复方式 |
|------|-------|--------|---------|---------|
| C-01 | 事实基座完整性 | BLOCKER | facts/目录不存在 | 创建facts/data.md |
| C-02 | 推论体系完整性 | ERROR | inferences/目录不存在 | 创建inferences/*.md |
| C-03 | 方案文件完整性 | ERROR | scheme/无文件 | 编辑scheme/*.md |
| C-04 | 事实可追溯 | WARN | 事实编号在方案中未被引用 | 添加编号引用 |
| C-05 | 断言可追溯 | WARN | <30%断言有编号 | 添加编号引用 |
| C-06 | 可证伪性 | WARN | <15%预测有条件句 | 添加"如果...则..." |
| C-07 | ID合规 | WARN | 非标准前缀 | 改用标准前缀 |
| C-08 | 引擎自检 | BLOCKER | derive.py不可运行 | 修复引擎 |

### 4.3 规约处理优先级

```
BLOCKER → 立即修复, 不修复不继续
ERROR   → 本轮修复, 影响方案完整性
WARN    → 记录, 后续迭代处理
```

---

## 五、自举验证

### 5.1 什么是自举

OntoDerive 能用自身的规约检查来验证描述自身的文档。

### 5.2 验证方式

```bash
# 对技术方案自验证
python3 engine/derive.py --project self-verify/docs --check

# 对全量框架自验证
python3 engine/derive.py --project self-verify/full --check
```

### 5.3 自举发现的典型缺口

| 轮次 | 发现 | 修复 |
|------|------|------|
| 1 | 元类型8→10不足(缺PROBABILISTIC+METRIC) | 更新元模型 |
| 2 | ID前缀不足(缺META-/TH-/BAY-等) | 扩展V2_ID_PATTERNS |
| 3 | 断言追溯率25% | 补充3W引言编号 |
| 4 | INF-v2-格式未在标准前缀 | 更新引擎模式 |

---

## 六、快速启动

### 6.1 最小可行项目结构

```
my-project/
├── facts/
│   ├── data.md       # 数据事实表(D-F1, D-F2, ...)
│   └── policy.md     # 政策事实表(P-F1, P-F2, ...)
├── entities/
│   └── actors.md     # 组织/角色实体(ORG-, ROL-, PRJ-)
├── inferences/
│   └── analysis.md   # 推论(INF-xx, 标注derives_from)
└── scheme/
    └── report.md     # 方案产出(断言标注编号)
```

### 6.2 三步上手

```bash
# 1. 初始化
python3 engine/derive.py --init my-project

# 2. 填充事实+实体+推论+方案

# 3. 验证
python3 engine/derive.py --project my-project --derive --check
python3 engine/derive.py --project my-project --rounds 3
```

---

## 七、扩展指南

### 7.1 新增元类型

1. 在 `framework/01-元模型/00-元模型定义.md` 的类型表中新增行
2. 在 `engine/derive.py` 的 `V2_ID_PATTERNS` 中添加对应前缀
3. 在 `ns/NAMESPACE.md` 中添加领域映射
4. 创建对应的实体实例验证测试

### 7.2 新增规约

1. 在 `engine/derive.py` 的 `check()` 方法中新增C-xx代码块
2. 确定严重度(BLOCKER/ERROR/WARN)
3. 实现检查逻辑和修复建议
4. 在 `self-verify/` 中新增对应的验证用例

### 7.3 适配新领域

1. 创建领域目录, 填充 facts/entities/inferences/scheme
2. 确保所有实体使用标准ID前缀
3. 每个推论标注 `derives_from` 事实编号
4. 方案中的每个断言引用对应编号
5. 运行 `--rounds 3` 收敛
6. 提交Git, 记录版本快照

---

## 八、与国转中心方案的关系

OntoDerive 从国转中心数字化平台方案的实战中蒸馏。

国转中心方案是 OntoDerive 的第一个完整实例：
- 27个SSOT文件, 3116行
- 19条规约, 5条推理规则
- 6层本体建模, 8类元类型(后扩展为10)
- 4份主文档+6份附录, 全部可追溯

国转中心方案验证了 OntoDerive 在复杂政府数字化项目中的适用性。
如果有人想复现类似的方案，流程是：

```bash
python3 engine/derive.py --init guozhuan-platform
# 填充470项成果/133名经理人/220亿基金等事实
# 建立L1-L6矛盾诊断
# 推导四根支柱→八步流程→业务飞轮
python3 engine/derive.py --project guozhuan-platform --rounds 5
```
