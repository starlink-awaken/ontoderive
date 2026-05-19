# 知识工程推导模式全景

> 调研适用于OntoDerive的推理/推导模式。每种模式标注了是否可无LLM实现。

---

## 一、古典逻辑 (Classical Logic)

### 1.1 三段论 (Syllogism) — 已实现
```
大前提: 所有A是B
小前提: X是A
结论:   X是B

OntoDerive: RuleReasoner.R3 缺失引用检测
```

### 1.2 假言推理 (Modus Ponens/Tollens) — 可实现
```
肯定式(MP): A→B, A ∴ B
否定式(MT): A→B, ¬B ∴ ¬A

OntoDerive应用:
  IF 推论标注了 derives_from THEN 推论可信度更高
  推论A未标注 derives_from → 推论A可信度存疑
```

### 1.3 假言三段论 (Hypothetical Syllogism) — 可实现
```
A→B, B→C ∴ A→C

OntoDerive应用:
  INF-L1 derives_from D-F1 (D-F1→INF-L1)
  INF-L2 derives_from INF-L1 (INF-L1→INF-L2)
  ∴ INF-L2 间接依赖 D-F1
```

### 1.4 选言三段论 (Disjunctive Syllogism) — 部分可实现
```
A ∨ B, ¬A ∴ B

OntoDerive应用:
  "要么增加研发投入，要么增加营销投入"
  当前已增加营销 → ∴ 未增加研发
```

---

## 二、本体推理 (Ontology Reasoning)

### 2.1 包含推理 (Subsumption) — 可实现 ⭐
```
A ⊑ B (A是B的子类)
x ∈ A ∴ x ∈ B

OntoDerive应用:
  ORG-国转中心 ⊑ Organization (所有组织)
  Organization ⊑ Entity (所有组织都是实体)
  ∴ ORG-国转中心是Entity
```

### 2.2 属性传递 (Transitive Property) — 可实现
```
R(x,y) ∧ R(y,z) → R(x,z)

OntoDerive应用:
  derives_from(INF-L2, INF-L1) ∧ derives_from(INF-L1, D-F1)
  → indirectly_depends(INF-L2, D-F1)
```

### 2.3 域/值域约束 (Domain/Range) — TypeValidator已有
```
domain(derives_from) = Inference
range(derives_from) = Fact ∪ Inference
违反: derives_from(x, y) where y ∉ Fact ∪ Inference → ERROR
```

---

## 三、概率推理 (Probabilistic) — Bayesian已有

### 3.1 贝叶斯更新
### 3.2 马尔可夫链 (Markov Chain) — 可实现
```
当前状态 → 下一状态概率
P(T1→T2) = 0.7, P(T1→T3) = 0.3

OntoDerive应用:
  推导状态转移概率
  收敛检测
```

### 3.3 证据合成 (Dempster-Shafer)
```
多个证据源合成置信度
不需要先验概率
```

---

## 四、图推理 (Graph Reasoning)

### 4.1 影响传播 (Influence Propagation) — 可实现 ⭐
```
节点A对节点B的影响 = Σ (edges(A,B) × weight)

OntoDerive应用:
  D-F1变更 → 重新计算所有引用它的推论置信度
  依赖D-F1的推论最多(D-F1影响最大)
```

### 4.2 结构洞检测 (Structural Holes) — 可实现
```
社区间唯一连接点 = 瓶颈节点
移除瓶颈→ 信息流断裂

OntoDerive应用:
  哪个事实被最多推论依赖？(关键事实)
  哪个推论是连接两个知识群的唯一桥梁？
```

### 4.3 路径推导 (Path-based Inference)
```
A → B → C → D (如果A影响B,B影响C,C影响D,则A间接影响D)
影响衰减系数 = 0.9 × 0.9 × 0.9 = 0.729
```

---

## 五、时态推理 (Temporal Reasoning)

### 5.1 Allen区间代数 (13种关系) — 部分可实现
```
Before(A,B)    A在B之前
After(A,B)     A在B之后(即Before的反)
Meets(A,B)     A紧接B
Overlaps(A,B)  A与B重叠
...

OntoDerive应用:
  事实有时间戳 → 检测"新事实推翻旧推论"
  政策发布时间 → 检测"推论基于已废止政策"
```

### 5.2 变化检测 (Change Detection)
```
D-F1(t0) = 100, D-F1(t1) = 150 → D-F1上升了50%
此前INF-L1基于D-F1=100 → 需要重新评估
```

---

## 六、操作推理 (Operational Reasoning)

### 6.1 约束传播 (Constraint Propagation)
```
C-05要求断言追溯率 >= 30%
当前追溯率 = 15% → 触发改善建议
```

### 6.2 区间算术 (Interval Arithmetic)
```
D-F1 ∈ [100, 200], D-F2 ∈ [300, 500]
D-F1 + D-F2 ∈ [400, 700]
```

### 6.3 依赖图重算 (Dependency Graph Recalculation)
```
事实变更 → 标记所有依赖它的推论为 stale
→ 按拓扑序重新计算
```

---

## 七、类比推理 (Analogical) — 需要LLM

### 7.1 案例推理 (Case-Based Reasoning)
```
案例1(市场进入): SWOT → PEST → 波特五力 → 成功
新案例(市场进入): 相似特征 → 推荐相似方法论序列
```

### 7.2 溯因推理 (Abduction)
```
观察: KQI下降而事实数不变
最可能原因: 推论质量下降
→ 检查最近修改的推论
```

---

## 八、结构推理 (Structural Reasoning)

### 8.1 冗余检测 (Redundancy)
```
INF-L1和INF-L2结论相似，引用同一事实
→ 可能是重复推论，建议合并
```

### 8.2 覆盖度分析 (Coverage Analysis)
```
D-F1~D-F10共10个事实
推论引用覆盖 = 6/10 = 60%
未被引用的: D-F3, D-F5, D-F7, D-F9 → 这些数据可能是冗余的
```

### 8.3 一致性分析 (Consistency)
```
所有推论置信度 > 0.85
但KQI仅0.33
→ 置信度评分与KQI脱节，评分体系不一致
```

---

## 实施优先级

| 优先级 | 模式 | 价值 | 成本 | 状态 |
|--------|------|------|------|------|
| P0 | 假言推理 (MP/MT) | 高 | 低 | 待实现 |
| P0 | 传递推理 (属性链) | 高 | 低 | 待实现 |
| P1 | 影响传播 (图) | 高 | 中 | 待实现 |
| P1 | 时态推理 | 中 | 中 | 待实现 |
| P1 | 包含推理 (本体) | 高 | 中 | 待实现 |
| P2 | 选言三段论 | 中 | 高 | 待调研 |
| P2 | 结构洞检测 | 中 | 中 | 待实现 |
| P3 | 案例推理 | 中 | 高 | 需LLM |
| P3 | 溯因推理 | 高 | 高 | 需LLM |

---

## 不可实现的界限

| 需要的能力 | 为什么不可无LLM实现 |
|-----------|------------------|
| 自然语言理解 | "当前阶段应该" → "建议优先级" 需要语义理解 |
| 隐喻/类比创造 | "像飞轮一样" → 需要概念映射创造力 |
| 价值判断 | "这个推论更重要" → 需要理解上下文和目标 |
| 新概念发现 | "市场进入壁垒" → 需要领域知识综合 |
