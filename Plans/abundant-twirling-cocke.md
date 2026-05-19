# OntoDerive v4.0 — 形式化知识推理引擎

## Context

当前v3.2的核心局限：`derive()`做的是结构分析（文件扫描+计数+模式匹配），不做真正的逻辑推理。矛盾检测覆盖率~6%（词对法），深度学习需要LLM但不能替代确定性推理。

用户提出的正确方向：**原始信息→本体对齐→符号化→形式推理→结论**。这是知识工程40年验证过的标准范式。LLM在两端（自然语言理解/生成），形式推理在中间（确定性可审计）。

## 目标架构

```
                    ┌─────────────┐
  原始研究信息 ────→│ Phase 1      │
  (自然语言文本)     │ LLM提取      │ Prompt: 提取事实/实体/推论/时间线
                    │ + 规则校验    │ TypeValidator + ContentCanonicalizer
                    └──────┬──────┘
                           │ 结构化数据
                           ▼
                    ┌─────────────┐
                    │ Phase 2      │
                    │ 本体对齐      │ ABox(事实实例) + TBox(类型层级)
                    │ 符号化        │ OntoLang v3 形式语言
                    └──────┬──────┘
                           │ ABox + TBox
                           ▼
                    ┌─────────────┐
                    │ Phase 3      │
                    │ 形式推理      │ 描述逻辑+三段论+假言+约束传播
                    │ (零LLM)      │ 输出: 新事实/新推论/矛盾/不确定性
                    └──────┬──────┘
                           │ 推理结论(逻辑符号)
                           ▼
                    ┌─────────────┐
                    │ Phase 4      │
                    │ LLM解读      │ 逻辑结论→自然语言报告
                    │              │ 区分: 确定结论/推测建议/不确定性
                    └─────────────┘
                           │
                           ▼
                    用户可读的分析报告
```

## 新增模块

### engine/formalize.py — 符号化引擎

```
Formalizer:
  extract_from_text(raw_text) → structured_facts, entities, inferences
    调用LLM: 从自然语言提取结构化知识
    调用TypeValidator: 校验ID格式
    调用ContentCanonicalizer: 范式化数值/时间戳

  to_ontolang(data) → OntoLang AST
    结构化数据→OntoLang v3 AST
    支持: fact/entity/inference/relation/protocol声明

  from_ontolang(ast) → markdown
    逆转换: AST→人类可读的Markdown
```

### engine/reasoner_formal.py — 形式推理引擎

```
FormalReasoner:
  输入: ABox(facts) + TBox(type hierarchy) + 推理规则
  输出: 新结论 + 矛盾 + 不确定性标注

  推理规则:
    R1 包含推理: X ⊑ Y, individual ∈ X → individual ∈ Y
    R2 传递推理: R(X,Y) ∧ R(Y,Z) → R(X,Z)
    R3 约束传播: 规约阈值 → 违反标记
    R4 等价替换: A ≡ B → 所有A可替换为B
    R5 实例归类: individual properties → 推断其所属类别

  输出标注:
    [确定] 逻辑必然结论
    [推测] 基于缺省规则的推测
    [不确定] 证据不足以判断
```

### engine/pipeline_v4.py — 四阶段管线

```
FormalPipeline:
  Phase1Stage: LLM提取 → structured_data
  Phase2Stage: 符号化 → ontolang_ast (ABox + TBox)
  Phase3Stage: 形式推理 → conclusions (确定/推测/不确定)
  Phase4Stage: LLM解读 → report (markdown)
```

## 已有可复用组件

| 组件 | 文件 | 在新架构中的角色 |
|------|------|----------------|
| TypeValidator | typesystem.py | Phase1/2: 校验符号化后的ID |
| ContentCanonicalizer | reasoning.py | Phase1: 范式化提取结果 |
| OntoLang Parser | ontolang/ | Phase2: 符号化表示 |
| RuleReasoner(R1-R21) | reasoner.py | Phase3: 部分确定性推理 |
| InsightEngine | insight.py | Phase4: LLM解读 |
| PromptTemplate | prompts.py | Phase1/4: LLM提取/解读提示词 |
| EntailmentGraph | logic.py | Phase3: 图推理可视化 |
| CachedReader | utils.py | Phase1: 缓存文件读取 |

## 实施路线

### Sprint 1: 最小闭环 (3天)

```
目标: 输入一段文本, 输出符号化事实+1条推导
新文件: engine/formalize.py (Formalizer), engine/reasoner_formal.py (FormalReasoner)
修改: 无破坏性修改
验收: 5条E2E测试
```

### Sprint 2: 四阶段管线 (2天)

```
目标: FormalPipeline四阶段全通
新文件: engine/pipeline_v4.py
验收: 管道端到端测试
```

### Sprint 3: LLM解读 (2天)

```
目标: LLM解读形式推理结果→自然语言报告
验收: 报告包含确定/推测/不确定分类
```

### Sprint 4: 文档+案例 (1天)

```
目标: 完整文档+可运行案例
验收: AGENTS.md/USER_GUIDE更新, demo-formal案例
```

## 验收标准

- `python3 -m pytest tests/ -q` — 168+ passed
- 输入一段原始文本, 输出含确定/推测/不确定标注的推导报告
- 形式推理部分零LLM, 确定性可复现
- 向后兼容: derive()/check()继续工作