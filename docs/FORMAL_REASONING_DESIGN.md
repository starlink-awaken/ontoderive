# 形式化推理引擎设计

> 基于用户提出的"本体对齐→符号化→逻辑推理"管线

---

## 架构

```
用户输入原始信息
     │
     ▼
[Phase 1: LLM提取]      自然语言 → 结构化事实/实体/推论
     │                   Prompt: "从以下研究报告中提取..."
     │                   输出: 事实表 + 实体表 + 推论表
     ▼
[Phase 2: 本体对齐]      结构化数据 → 形式化符号
     │                   TypeValidator: ID→MetaType
     │                   OntologyMapper: 实体→TBox归类
     │                   输出: ABox + TBox
     ▼
[Phase 3: 符号推理]      形式符号 → 逻辑蕴含
     │                   描述逻辑推理: 包含/传递/等价
     │                   规则推理: 三段论/假言/选言
     │                   输出: 新事实 + 新推论 + 矛盾
     ▼
[Phase 4: LLM解读]       形式结论 → 自然语言
     │                   Prompt: "将以下逻辑结论翻译为决策建议"
     │                   输出: 用户可读的推导报告
```

---

## 形式化语言设计

### 事实符号化

```
原始:
  "公司年营收2.3亿, 员工85人, 市场份额29%"

符号化 (OntoLang):
  fact D-F1 : Revenue { value: 2.3, unit: "亿", period: "annual" }
  fact D-F2 : Employee { count: 85 }
  fact D-F3 : MarketShare { value: 0.29, competitor: "竞品A" }

逻辑表示 (Description Logic):
  Company ⊓ ∃hasRevenue.≥2.0e8 ⊓ ∃hasEmployees.≤100
```

### 推论形式化

```
原始:
  "公司市场份额低, 应加大营销投入"

符号化:
  inference INF-L1 : Strategy {
    derives_from: [D-F3]
    antecedent: MarketShare(product, 0.29)
    consequent: Increase(marketing_budget)
    rule: low_market_share → increase_marketing
  }
```

### 推理规则形式化

```
规则1 (三段论):
  IF MarketShare(X, m) ∧ m < threshold
  THEN CompetitivePosition(X, weak)

规则2 (假言三段论):
  IF CompetitivePosition(X, weak)
  THEN Recommend(X, increase_marketing)
  
推导链:
  MarketShare(product, 0.29) → CompetitivePosition(product, weak)
  CompetitivePosition(product, weak) → Recommend(increase_marketing)
  ∴ Recommend(product, increase_marketing)
```

---

## 与现有RuleReasoner的对比

| 维度 | 当前RuleReasoner | 形式推理引擎 |
|------|-----------------|------------|
| 输入 | 字符串匹配 | 符号化事实 |
| 推理方式 | 正则+条件判断 | 逻辑蕴含演算 |
| 可验证性 | 难以验证规则是否正确 | 推理步骤可逐行检查 |
| 可扩展性 | 每条新规则需要写代码 | 新规则是声明式逻辑语句 |
| 表达能力 | 限于预定义模式 | 组合爆炸 (但可管理) |
| LLM依赖 | 零依赖 | Phase 1和4需要LLM, Phase 2-3零LLM |

---

## 可实现的边界

### ✅ 可实现 (确定性推理)

1. **数值比较**: A > B, B > C → A > C (传递性)
2. **属性继承**: X是Y的子类, Y有属性P → X有属性P
3. **约束满足**: 如果C-05要求追溯率≥30%且当前15% → 违反
4. **等价推导**: A等价于B, B等价于C → A等价于C
5. **分类推理**: 所有D-F事实都是FACT类型 → D-F1是FACT

### ⚠️ 部分可实现 (需要领域知识)

1. **因果推理**: A导致B, B导致C → A导致C (需要因果模型)
2. **时序推理**: A在B之前, B在C之前 → A在C之前 (需要时间戳)
3. **缺省推理**: 通常A为真, 除非有反例 → A tentatively true

### ❌ 不可实现 (需要语义理解)

1. **隐喻推理**: "像飞轮一样" → 需要理解隐喻
2. **价值判断**: "这个决策更好" → 需要价值体系
3. **创造性发现**: "市场存在未被满足的需求" → 需要领域创新

---

## 实施路线

### Phase A: 形式化语言 (1周)
- 设计OntoLang v3: 支持逻辑规则声明
- 实现符号化器: 结构化数据→OntoLang AST
- 实现反符号化器: OntoLang AST→自然语言

### Phase B: 推理引擎 (1周)
- 实现描述逻辑基础推理 (包含/传递/等价)
- 实现规则引擎事实化 (现有RuleReasoner输出→形式推理格式)
- 实现推理链可视化

### Phase C: LLM集成 (1周)
- Phase 1: LLM提取原始信息→结构化事实/实体/推论
- Phase 4: LLM解读推理结果→自然语言报告
- 全管线集成测试
