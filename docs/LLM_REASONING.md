# LLM推理模式深度调研

> 适用于OntoDerive的LLM推理增强方法。每种方法评估适用性和实现成本。

---

## 一、Chain-of-Thought (CoT) — 已集成

```
提示词: "让我们一步步思考..."
效果: LLM展示推理步骤, 减少跳跃性错误
成本: ~2x tokens
OntoDerive: prompts.py 已有 chain_of_thought=True 配置
```

## 二、Tree-of-Thoughts (ToT) — 可集成 ⭐

```
思想: 同时探索多个推理路径, 剪枝后选最优
流程: 生成N个候选推论 → 评估每个 → 保留Top-K → 继续下一层
适用: 矛盾检测(探索双方推理链), 质量评估(多角度评分取中位数)
成本: ~5x tokens
```

**OntoDerive集成方案**:
```python
def tot_derive(facts, inferences, branching=3, depth=2):
    insights = []
    for _ in range(depth):
        candidates = [llm_derive_with_prompt(p) for p in varied_prompts]
        scored = [(c, llm_score(c)) for c in candidates]
        insights.extend(sorted(scored, key=lambda x: -x[1])[:branching])
    return insights
```

## 三、ReAct (Reasoning + Acting) — 可集成 ⭐⭐

```
思想: 推理和行动交替进行
流程: 观察(事实) → 思考(推理) → 行动(检查引用) → 观察(结果) → 重复
适用: 事实追溯验证, 推导链完整性检查
成本: ~3x tokens
```

**OntoDerive集成方案**:
```
ReAct循环:
  1. Thought: "INF-L1引用了D-F1, 需要验证D-F1的值"
  2. Action: read_fact("D-F1")
  3. Observation: "D-F1=500万日活"
  4. Thought: "500万相对1200万竞品, 市场份额29%, 推论合理"
  5. Action: mark_verified("INF-L1", confidence=0.85)
```

## 四、Self-Consistency — 可集成 ⭐

```
思想: 采样N条推理路径, 多数投票或取平均
效果: 减少单次推理的随机性
适用: 质量评分(3次取中位数), 矛盾检测(3次过半数判定)
成本: ~3x tokens
```

**OntoDerive集成方案**:
```python
def self_consistent_judge(project, n_samples=3):
    scores = [judge_project(project) for _ in range(n_samples)]
    return {
        "score": statistics.median([s["score"] for s in scores]),
        "consensus": all(s["verdict"] == scores[0]["verdict"] for s in scores),
    }
```

## 五、Reflexion — 可集成 ⭐

```
思想: LLM反思自己的输出, 自我修正
流程: 生成 → 自我评估 → 发现问题 → 修正 → 重新生成
适用: 推导洞察的自我校验, 质量评估的二次确认
成本: ~2-3x tokens
```

## 六、Graph-of-Thoughts (GoT) — 可集成 ⭐⭐

```
思想: 多个推理链可以合并、分支、循环
与OntoDerive的蕴含图天然契合!
流程: 事实节点 → 推论节点 → (合并) → 综合节点
适用: 多推论综合分析, 知识图谱增强推理
成本: ~4x tokens
```

**OntoDerive集成方案**:
```python
def got_analyze(entailment_graph):
    # 从蕴含图的叶节点(最终推论)出发
    # 沿derives_from反向传播分析
    # 在合并节点处综合多路推理
    for leaf in graph.leaf_nodes():
        paths = graph.all_paths_to_root(leaf)
        merged = llm_merge_paths(paths)  # LLM综合多路径
```

## 七、Multi-Agent Debate — 可集成 ⭐

```
思想: 多个LLM实例(或同一LLM不同角色)辩论
流程: Agent A提出推论 → Agent B反驳 → Agent C仲裁
适用: 矛盾检测(双方辩论), 质量评估(多角色评审)
成本: ~4x tokens
```

## 八、Structured CoT — 可集成

```
思想: 让LLM输出结构化JSON而非自由文本
效果: 提高解析成功率, 减少幻觉
OntoDerive: prompts.py 已使用 output_format="json"
```

---

## 实施优先级

| 方法 | 价值 | 成本 | 实施难度 | 推荐 |
|------|------|------|---------|------|
| CoT | 高 | 低 | 已集成 | ✅ |
| Structured Output | 高 | 低 | 已集成 | ✅ |
| Self-Consistency | 高 | 低 | 低 | ⭐ 优先 |
| Reflexion | 高 | 中 | 中 | ⭐ 优先 |
| ReAct | 高 | 中 | 中 | ⭐⭐ 适合事实追溯 |
| GoT | 很高 | 中 | 中 | ⭐⭐ 与蕴含图天然契合 |
| ToT | 高 | 高 | 高 | 适合矛盾检测 |
| Multi-Agent | 很高 | 很高 | 高 | 适合深度评审 |

---

## 推荐路线

**Phase 1 (本周)**: Self-Consistency + Reflexion
- 在judge.py中加3次采样取中位数
- 在insight.py中加自我反思修正

**Phase 2 (下周)**: ReAct + GoT  
- ReAct用于事实追溯自动化
- GoT与蕴含图结合做多路径综合

**Phase 3 (后续)**: Multi-Agent Debate
- 矛盾检测升级为辩论模式
