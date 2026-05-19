# 图凝聚度提升 — 从0.10→0.15+架构重构

## Context

知识图谱显示68社区凝聚度0.05-0.10。根因：`check.py`的`run_check()`是270行god-function，直接导入6个理论模块，形成dense hub-and-spoke图结构。这不是bug而是当前架构的必然结果。

## 架构方案：Strategy Pattern + Theory Check Registry

核心思路：不减少连接（规约检查必须调用所有理论），而是**让连接更有序**。每个理论检查变成独立可插拔的策略单元。

### 目标架构

```
Before (hub-and-spoke, 凝聚力0.05):
  check.py ──→ bayesian.py
          ├──→ metrics.py
          ├──→ controller.py
          ├──→ turing_k.py
          ├──→ ontolang.py
          └──→ typesystem.py

After (strategy chain, 凝聚力目标0.15):
  check.py ──→ check_theory.py (C-09~C-13 registry)
                    ├── C-09 → BayesianLayer (独立函数, 暴露check接口)
                    ├── C-10 → MetricsLayer
                    ├── C-11 → PIDController
                    ├── C-12 → KnowledgeTM
                    └── C-13 → OntoLangParser
```

### 关键重构

1. **提取check_theory.py**：从check.py分离C-09~C-13（~120行）
2. **理论模块暴露check方法**：每个模块添加`check_xxx(root)`静态函数
3. **check.py瘦身**：270→~150行，C-01~C-08保留（文件检查，轻量正则）

## 验收

- `python3 -m pytest tests/ -q` — 150+通过
- 重新运行graphify AST提取，中位凝聚度≥0.15
- check.py < 160行
- 理论模块各有独立`check_xxx()`公开函数
