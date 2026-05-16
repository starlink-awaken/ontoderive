# OntoDerive — 渊衍框架

> **事实驱动的一体化知识工程与方案推导框架**
>
> 从"事实 → 本体 → 推论 → 方案"的全链路可追溯推导。
> 核心能力：元建模 + 正向推导 + 反向规约校验 + 多轮迭代收敛 + 自举验证。

[![Version](https://img.shields.io/badge/version-1.2.0-blue)](engine/derive.py)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-orange)]()

---

## 🎯 核心价值

一次从数据到方案的推导循环：

```python
python3 engine/derive.py --init my-project  # 2分钟建立项目骨架
# 编辑 facts/data.md, entities/actors.md, inferences/design.md
python3 engine/derive.py --project my-project --derive --check  # 推导+验证
```

**解决的核心问题**：方案文档的断言是否可追溯？关键判断是否可证伪？事实是否被正确引用？

## 🏗️ 架构

```
MOF四层             六层能力
────────            ────────
M3: 元元模型层  ←→  控制论·信息论·贝叶斯·逻辑·形式语言·本体核
M2: 元模型层        10元类型 · 4元关系 · 4元约束
M1: 领域模型层       TBox + ABox (实体实例)
M0: 实例/数据层      D-Fx事实 + P-Fx政策
```

## 📦 快速开始

```bash
# 克隆
git clone https://github.com/your-org/ontoderive.git
cd ontoderive

# 体验内置示例
python3 engine/derive.py --project examples/z-park --derive --check --generate report
cat examples/z-park/_derivation_logs/report.md

# 初始化自己的项目
python3 engine/derive.py --init my-project
```

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 项目入口(agent标准操作流程) |
| [ns/NAMESPACE.md](ns/NAMESPACE.md) | 命名空间与实体ID规范 |
| [framework/01-元模型/00-元模型定义.md](framework/01-元模型/00-元模型定义.md) | 10元类型定义 |
| [framework/02-迭代方案-v2.md](framework/02-迭代方案-v2.md) | v2设计方案(七论融合) |
| [engine/derive.py](engine/derive.py) | 推导引擎(v1.2.0, 8规约) |
| [examples/z-park](examples/z-park) | 完整示例 |
| [self-verify/docs](self-verify/docs) | 自举验证 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

## 🔬 验证

OntoDerive 通过了自举验证——它验证了描述自身的技术方案文档：

```bash
python3 engine/derive.py --project self-verify/docs --check
# 7/8 规约通过, 30事实100%追溯, 断言75%可追溯
```

## 📊 统计

| 指标 | 数值 |
|------|------|
| 核心引擎 | ~600行 Python |
| 元类型 | 10 (DOMAIN/FACT/INFERENCE/...) |
| 规约 | 8条 |
| ID前缀 | 26种 |
| 框架代码 | ~1500行 (含文档和示例) |

## 🔗 与其他项目的关系

OntoDerive 是从[国转中心数字化平台方案](https://github.com/your-org/guozhuan-center)的实战中蒸馏出的通用框架。
国转中心方案是 OntoDerive 的第一个完整实例(27个SSOT文件, 19条规约, 5条推理规则)。

## 📄 License

MIT
