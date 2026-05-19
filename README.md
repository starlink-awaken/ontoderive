# OntoDerive — 渊衍框架 v3.1

> **知识工程分析平台** — 双模式：结构分析(无LLM) + 洞察推导(需LLM)
>
> 从"工具匹配 → 事实 → 本体 → 推论 → 方案"的全链路可追溯分析。
> 核心能力：ToolForge工具匹配 + 元建模 + 正向推导 + 反向规约校验 + 多轮迭代收敛 + 自举验证。

[![Version](https://img.shields.io/badge/version-3.3.0-blue)](engine/derive.py)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-orange)]()

---

## 🎯 核心价值

一次从目标到方案的完整推导循环：

```bash
# 带工具匹配的完整推导（v2.0 新增）
python3 engine/derive.py --project my-project --with-tools --goal "分析目标" --derive --check

# 独立工具匹配
python3 engine/toolforge/matcher.py "分析新能源汽车市场" --inference-guide
```

**解决的核心问题**：该用什么思维框架？方案断言是否可追溯？关键判断是否可证伪？事实是否被正确引用？

## 🏗️ 架构

```
ToolForge前置 → MOF四层 → 六层能力
  (工具匹配)      ────────   ────────
              M3: 元元模型层  ←→  控制论·信息论·贝叶斯·逻辑·形式语言·本体核
              M2: 元模型层      10元类型 · 4元关系 · 4元约束
              M1: 领域模型层     TBox + ABox (实体实例)
              M0: 实例/数据层    D-Fx事实 + P-Fx政策
```

## 📦 快速开始

```bash
# 克隆
git clone https://github.com/your-org/ontoderive.git
cd ontoderive

# 体验内置示例（带工具匹配）
python3 engine/derive.py --project examples/z-park --with-tools --goal "中关村科技园区" --derive --check

# 初始化自己的项目
python3 engine/derive.py --init my-project
```

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 项目入口(agent标准操作流程) |
| [docs/MANIFESTO.md](docs/MANIFESTO.md) | 渊衍纲领(含ToolForge前置匹配) |
| [ns/NAMESPACE.md](ns/NAMESPACE.md) | 命名空间与实体ID规范 |
| [framework/01-元模型/00-元模型定义.md](framework/01-元模型/00-元模型定义.md) | 10元类型定义 |
| [framework/02-迭代方案-v2.md](framework/02-迭代方案-v2.md) | v2设计方案(七论融合) |
| [engine/derive.py](engine/derive.py) | 推导引擎(v1.4.0, 13协议) |
| [engine/toolforge/README.md](engine/toolforge/README.md) | ToolForge工具匹配模块 |
| [examples/z-park](examples/z-park) | 完整示例 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

## 🔬 验证

```bash
python3 engine/derive.py --project self-verify/docs --check
# 13/13 规约通过
```

## 📊 统计

| 指标 | 数值 |
|------|------|
| 核心引擎 | ~5,200行 Python (25模块+5子包) |
| ToolForge 匹配引擎 | TF-IDF + keyword + hybrid 三模式 |
| 元类型 | 10 (DOMAIN/FACT/INFERENCE/STATE/DOCUMENT/CONSTRAINT/PROCESSOR) |
| 规约 | 13条 (C-01 ~ C-13) |
| 测试 | 114个，全部通过 |
| 思维工具目录 | 73工具 (6维度) |
| MCP工具总数 | 11 (统一入口) |
| 生态适配器 | Minerva / Sophia / Agora / eCOS |

## 🔗 生态协作

```
Minerva (深度研究) → Sophia (范式引擎, 已内置)
                        ↓
                  ToolForge (工具匹配) → OntoDerive (事实推导)
                        ↓                       ↓
                  Agora (MCP路由层) ←────────────┘
                        ↓
                  eCOS (Agent编排 + 认知运行时)
```

## 📄 License

MIT
