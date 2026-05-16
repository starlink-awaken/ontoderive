---
name: ontoderive
description: >
  OntoDerive 渊衍框架——事实驱动的一体化知识工程与方案推导。
  从"事实→本体→推论→方案"的全链路可追溯推导。
  核心能力：元建模、正向推导、反向规约校验、多轮迭代收敛。
triggers:
  - "/ontoderive"
  - "渊衍框架"
  - "事实驱动推导"
  - "从事实到方案"
  - "知识工程框架"
  - "初始化推导项目"
  - "执行规约检查"
  - "运行多轮迭代"
---

# OntoDerive — 渊衍框架

## 一句话定位

把任何领域的事实，推导为可验证的方案——且每一步都可追溯、可证伪、可自动化。

## 核心推导链

```
事实基座(What is) → 本体模型(What exists)
    → 推论体系(What follows) → 方案文档(What to do)
        ↑                        ↓
    └──────── 双向规约校验 ────────┘
```

## 标准操作流程

### 第1步：初始化项目

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 engine/derive.py --init my-project
```

### 第2步：读取方法论

依次阅读：
1. `framework/01-元模型/00-元模型定义.md` — 8元类型×4元关系×4元约束
2. `examples/z-park/README.md` — 通过示例理解完整流程
3. `examples/z-park/facts/data.md` — 事实基座格式
4. `examples/z-park/inferences/contradictions.md` — 推论格式

### 第3步：填充项目内容

```
my-project/
├── facts/data.md         ← 数据事实表(D-Fx)
├── facts/policy.md       ← 政策事实表(P-Fx)
├── entities/actors.md    ← 实体定义(ORG-/ROL-/PRJ-)
├── inferences/           ← 推论(矛盾的+L推导)
└── scheme/               ← 方案产出
```

### 第4步：执行推导引擎

```bash
python3 engine/derive.py --project my-project --derive  # 正向推导
python3 engine/derive.py --project my-project --check   # 规约检查
python3 engine/derive.py --project my-project --rounds 3  # 多轮迭代
python3 engine/derive.py --project my-project --generate report  # 报告
```

## 8条规约检查项

| 编号 | 检查项 | 严重度 | 说明 |
|------|-------|--------|------|
| C-01 | 事实基座完整性 | BLOCKER | facts/目录必须存在 |
| C-02 | 推论体系完整性 | ERROR | inferences/目录必须存在 |
| C-03 | 方案文件完整性 | ERROR | scheme/目录必须有文件 |
| C-04 | 事实可追溯性 | WARN | 事实编号在推论和方案中被引用 |
| C-05 | 断言可追溯性 | WARN | 含"应该/必须/需要"的句子旁标注编号 |
| C-06 | 关键判断可证伪性 | WARN | 核心预测附带"如果X则Y"条件 |
| C-07 | 实体ID合规性 | WARN | 使用标准前缀(ORG-/ROL-/PRJ-) |
| C-08 | 推导引擎健康度 | BLOCKER | 引擎脚本正常可运行 |

## 核心约束

1. **事实先于推论**：没有事实编号的推论不被采用
2. **可证伪**：每个关键判断必须附带退出条件
3. **正交分解**：维度之间互不重叠
4. **双向闭环**：正向推导+反向校验=完整循环

## 快速体验内置示例

```bash
cd ${CLAUDE_PLUGIN_ROOT}
python3 engine/derive.py --project examples/z-park --derive --check --generate report
cat examples/z-park/_derivation_logs/report.md
```
