# OntoDerive v2.1 — 从Demo到真正可推导的知识工程引擎

> ISA v1.0 | E3 Tier | 2026-05-18  
> 承接 Phase 0-4 工程基座，攻坚审计发现的五个硬骨头

---

## Problem

当前OntoDerive已具备完善的工程基座（67测试、共享工具、数据模型、Pipeline、六论模块），但核心推导能力名不副实：

1. **`derive()` 不做推导** — 只做正则扫描+计数，是`wc -l`级别的统计，不是知识推导
2. **MOF四层只在文档中** — `framework/02-迭代方案-v2.md` 写了600行精密设计，代码中无分层类型系统
3. **六论数据流断裂** — 贝叶斯→信息论→控制论通过文件系统传递数据，各自重新实例化，无运行时管道
4. **测试缺口大** — Pipeline、ecosystem适配器、MCP server、watcher、extractor、cli 零测试覆盖
5. **文档与代码脱节** — framework文档声称的功能70%未实现，无实现状态标注
6. **默认行为不友好** — TF-IDF中文分词弱默认无结果，PID历史数据始终为空

这些问题的共同根因：Phase 0-4解决了"工程卫生"问题，但未触及"核心能力"问题。

---

## Vision

OntoDerive v2.1是一个**真正可推导**的知识工程引擎：
- 输入：一个项目目录（facts/entities/inferences/scheme四件套）
- 处理：通过MOF类型系统校验→贝叶斯信念传播→信息论KQI评估→控制论收敛→逻辑蕴含图分析的**实时数据管道**
- 输出：有依据的推导摘要+规约检查+置信度报告+改善建议，全程可追溯
- 开发体验：`pip install ontoderive && ontoderive analyze my-project` 一键全流程，所有模块有测试

---

## Out of Scope

- LLM集成（调用大语言模型做内容推导）— 留在v3.0
- 真正的符号推理/定理证明 — 留在v3.0
- 分布式/多进程Pipeline — 留在v3.0
- Web UI / 可视化Dashboard — 留在v3.0
- docx/pdf报告生成 — 留在v3.0
- 向上规约（从方案自动提取规约规则）— 留在v3.0
- 自演化学习（收敛速度追踪→规约调整）— 留在v3.0

---

## Principles

1. **真实优于花哨** — 每个模块的输出必须基于实际计算，不是硬编码或占位符
2. **数据流动** — 六论模块间通过内存传递数据，不再重新实例化或依赖文件系统中转
3. **测试即文档** — 每个公开接口必须有测试，测试覆盖即功能说明书
4. **渐进深挖** — 不推翻现有架构，在现有模块基础上深化实现
5. **中文可用** — 默认行为对中文用户友好（TF-IDF→keyword默认，分词优化）

---

## Constraints

- 零外部依赖：只用Python标准库 + 已存在的catalog.json
- 向后兼容：不破坏现有CLI/MCP/Python API接口
- 文件系统保留：facts/entities/inferences/scheme目录结构不变
- 测试先行：每个特性必须先有测试再实现

---

## Goal

将OntoDerive从"doc-checking正则扫描器"升级为"基于概率图模型和类型系统的可推导知识工程引擎"，使核心推导链（ToolForge→事实→类型校验→贝叶斯→KQI→PID→逻辑蕴含图）形成真正的运行时数据管道，并通过≥100个测试覆盖所有模块。

---

## Criteria

### 核心推导能力

- [ ] **ISC-1**: `derive()` 输出包含置信度分布和推导链统计，不仅是文件计数
  - Anti: `derive()` 输出中只有 `{"facts": N, "inferences": M}` 而没有置信度/链深度信息

- [ ] **ISC-2**: 运行 `ontoderive analyze examples/z-park` 后，Pipeline在内存中完成贝叶斯→KQI→PID的完整数据传递（不重新实例化BayesianLayer）
  - Anti: Pipeline执行期间metrics.py再次`from bayesian import BayesianLayer`重新扫描文件

### MOF类型系统

- [ ] **ISC-3**: 新增 `engine/typesystem.py`，实现10元类型(DOMAIN/FACT/INFERENCE/STATE/DOCUMENT/CONSTRAINT/PROCESSOR)的类型校验
  - Anti: 实体使用了非标准前缀但C-07不报告

- [ ] **ISC-4**: typesystem.py中的`TypeValidator.check()`方法能检测：类型不匹配、ID前缀与声明类型不一致、缺失必填属性

### 六论数据管道

- [ ] **ISC-5**: Pipeline一次运行中，BayesianLayer只实例化一次，其置信度输出被Metrics和PID直接消费（参数传递，不读文件）
  - Anti: 任何模块在Pipeline运行期间调用`all_md()`重新扫描facts/inferences目录

- [ ] **ISC-6**: PID历史数据来自`check-result-*.json`通配文件，运行`ontoderive check`三次后`_load_history()`返回≥2条记录

### 测试覆盖

- [ ] **ISC-7**: 总测试数 ≥ 100个，全部通过
  - Anti: 测试数<100或任何失败

- [ ] **ISC-8**: `tests/test_pipeline.py` 存在且覆盖DerivePipeline的端到端流程
- [ ] **ISC-9**: `tests/test_ecosystem.py` 存在且覆盖Minerva/Sophia/Agora/eCOS四个适配器
- [ ] **ISC-10**: `tests/test_mcp_server.py` 存在且验证全部11个MCP工具的响应格式

### 默认行为与文档

- [ ] **ISC-11**: `ToolForge().select("分析新能源汽车市场")` 默认返回≥3个结果（无需指定mode参数）
  - Anti: 默认`mode="tfidf"`返回空列表

- [ ] **ISC-12**: `framework/02-迭代方案-v2.md` 中每条设计声明标注实现状态（✅已实现/⚠️部分/❌待实现）

---

## Test Strategy

| ISC | Type | Check | Threshold | Tool |
|-----|------|-------|-----------|------|
| ISC-1 | unit | derive()输出包含confidence_distribution字段 | assert in | pytest |
| ISC-2 | integration | Pipeline run后metrics不再import bayesian | mock检测 | pytest+mock |
| ISC-3 | unit | typesystem.py TypeValidator类存在 | assert module | pytest |
| ISC-4 | unit | check()对无效类型返回ERROR | assert(len(errors)>0) | pytest |
| ISC-5 | integration | Pipeline执行期间bayesian实例化计数=1 | mock计数 | pytest+mock |
| ISC-6 | integration | 3次check后_load_history() >= 2条 | assert >= 2 | pytest |
| ISC-7 | unit | pytest tests/ -q 输出 ≥100 passed | grep count | pytest |
| ISC-8 | unit | test_pipeline.py 的test_e2e通过 | assert | pytest |
| ISC-9 | unit | test_ecosystem.py 覆盖4个适配器 | assert | pytest |
| ISC-10 | unit | test_mcp_server.py 验证11工具 | assert | pytest |
| ISC-11 | unit | select()默认返回≥3结果 | assert len>=3 | pytest |
| ISC-12 | manual | framework/02文件含✅/⚠️/❌标注 | grep count | grep |

---

## Features

| Name | Description | Satisfies | Depends On | Parallelizable |
|------|-------------|-----------|------------|----------------|
| **F1** derive升级 | derive()输出置信度分布+推导链统计；集成贝叶斯/KQI/PID结果 | ISC-1 | — | true |
| **F2** 类型系统 | engine/typesystem.py + 10元类型校验 + C-07/C-13检查升级 | ISC-3, ISC-4 | — | true |
| **F3** 六论数据管道 | Pipeline内存数据传递；Bayesian结果直传Metrics/PID；消除重复扫描 | ISC-2, ISC-5 | F1 | false |
| **F4** PID历史修复 | check结果存多份带时间戳文件；_load_history通配读取 | ISC-6 | — | true |
| **F5** Pipeline测试 | test_pipeline.py端到端测试 | ISC-8 | F3 | false |
| **F6** 生态测试 | test_ecosystem.py覆盖4适配器 | ISC-9 | — | true |
| **F7** MCP测试 | test_mcp_server.py验证11工具 | ISC-10 | — | true |
| **F8** 默认模式修复 | ToolForge默认keyword模式 | ISC-11 | — | true |
| **F9** 文档状态标注 | framework/02逐条标注实现状态 | ISC-12 | — | true |
| **F10** 补全测试 | 补watcher/extractor/cli/config测试至≥100 | ISC-7 | F5,F6,F7 | false |

### 执行顺序

```
F8(默认模式) + F4(PID历史) + F9(文档标注)  →  并行，1天
F1(derive升级) + F2(类型系统)              →  并行，2天
F3(六论管道)                                →  依赖F1，1天
F5(Pipeline测试) + F6(生态测试) + F7(MCP测试) → 并行，1.5天
F10(补全测试)                               →  依赖F5,F6,F7，1天
```

---

## Decisions

| 时间 | 决策 | 理由 |
|------|------|------|
| 2026-05-18 | 不引入LLM做内容推导 | 保持零外部依赖约束；LLM推导留给v3.0 |
| 2026-05-18 | 类型系统新建typesystem.py而非修改ontolang/ | 形式语言层处理语法，类型系统处理语义，职责分离 |
| 2026-05-18 | Bayesian暴露`get_distribution()`公开方法供Pipeline消费 | 避免metrics通过import重新扫描文件 |
| 2026-05-18 | 检查结果文件改为带时间戳存储 | PID需要历史数据；check-result.json保留兼容旧引用 |

---

## Verification

```bash
# ISC-7: 全量测试
python3 -m pytest tests/ -v
# 期望：≥100 passed, 0 failed

# ISC-1: derive升级验证
python3 -c "
from engine.derive import OntoDerive
od = OntoDerive('examples/z-park')
s = od.derive()
assert 'confidence_distribution' in s or 'chain_depth' in s, 'derive未升级'
print('ISC-1 OK')
"

# ISC-11: 默认模式验证
python3 -c "
from engine.toolforge.matcher import ToolForge
tf = ToolForge()
r = tf.select('分析新能源汽车市场')
assert len(r) >= 3, f'默认模式仅返回{len(r)}个结果'
print('ISC-11 OK')
"

# ISC-6: PID历史验证
python3 engine/derive.py --project examples/z-park --check
python3 engine/derive.py --project examples/z-park --check
python3 engine/derive.py --project examples/z-park --check
python3 -c "
from engine.controller import PIDController
ctrl = PIDController('examples/z-park')
assert len(ctrl.history) >= 2, f'PID历史仅{len(ctrl.history)}条'
print('ISC-6 OK')
"
```
