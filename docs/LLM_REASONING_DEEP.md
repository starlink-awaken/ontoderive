# LLM推理方法深度接入分析

> 评估 ReAct / GoT / ToT / Multi-Agent Debate 四种方法在OntoDerive现有架构中的可接入性。

---

## 一、ReAct — 推理+行动交替

### 1.1 方法本质

```
循环: Thought(思考) → Action(行动) → Observation(观察) → Thought → ...
关键: Action必须能调用外部工具, Observation来自工具返回
```

### 1.2 OntoDerive现有架构匹配度: 9/10 ⭐⭐

OntoDerive已有完整的"行动"系统，ReAct只需要让LLM调用这些行动：

```
可用Action(已存在):
  read_fact(D-F1)          → 返回事实值和来源
  read_inference(INF-L1)   → 返回推论全文+引用链  
  check_reference(INF-L1)  → 验证所有引用是否存在
  get_confidence(INF-L1)   → 返回贝叶斯传播后的置信度
  trace_chain(INF-L1)      → 追溯完整推导链
  find_contradictions()    → 运行矛盾检测
  compute_kqi()            → 计算KQI

Observation格式(已存在):
  {"fact": "D-F1", "value": "500万", "source": "运营后台"}
  {"inference": "INF-L1", "derives_from": [...], "confidence": 0.85}
  {"contradictions": [{"a": "INF-L1", "b": "INF-L2", "shared": ["D-F1"]}]}
```

### 1.3 接入方案

```python
# 新增 engine/intelligence/react.py
class ReActEngine:
    def __init__(self, project_root, enhancer):
        self.root = project_root
        self.llm = enhancer
        self.actions = {
            "read_fact": self._read_fact,
            "read_inference": self._read_inference,
            "check_reference": self._check_reference,
            "get_confidence": self._get_confidence,
            "trace_chain": self._trace_chain,
            "find_contradictions": self._find_contradictions,
            "compute_kqi": self._compute_kqi,
        }
        self.history = []  # [(thought, action, observation), ...]

    def run(self, query, max_steps=5):
        """ReAct主循环"""
        for step in range(max_steps):
            thought, action_name, action_arg = self._llm_decide(query, self.history)
            if action_name == "FINISH":
                return thought  # LLM自主决定结束
            observation = self.actions[action_name](action_arg)
            self.history.append((thought, action_name, observation))
```

**引导LLM使用ReAct的提示词**:
```
你可用的工具:
- read_fact(D-F1): 读取事实的值和来源
- read_inference(INF-L1): 读取推论全文和引用链
- check_reference(INF-L1): 验证推论的所有引用是否存在
- get_confidence(INF-L1): 获取贝叶斯传播置信度
- trace_chain(INF-L1): 追溯完整推导链
- find_contradictions(): 运行矛盾检测

每次响应格式:
Thought: [你的推理]
Action: [工具名](参数)

当分析完成时:
Thought: [最终结论]
Action: FINISH
```

### 1.4 价值评估

| 场景 | 无ReAct | 有ReAct |
|------|---------|---------|
| 验证INF-L1是否正确 | LLM猜测 | LLM调用read_fact确认 |
| 检查推导链完整性 | analyze()一次性 | ReAct逐步追溯 |
| 发现矛盾 | 依赖预计算 | LLM主动调用find_contradictions |

---

## 二、GoT (Graph of Thoughts) — 图思维

### 2.1 方法本质

```
传统CoT: A → B → C → D (线性链)
GoT:      A → B → C
              ↘ E → F ↗   (合并两条推理路径)
              ↘ G     ↗   (分支再收敛)
```

### 2.2 OntoDerive现有架构匹配度: 10/10 ⭐⭐⭐

OntoDerive的核心数据结构就是**图**！这是最天然的契合。

```
已有图结构:
  BayesianNetwork (bayesian.py)    — DAG节点+边, 拓扑序, 信度传播
  EntailmentGraph (logic.py)       — 推导链, 环检测, 瓶颈检测
  DerivePipeline (pipeline.py)     — 六阶段DAG

GoT只需利用这些已有图结构, 让LLM在图上游走推理。
```

### 2.3 接入方案

```python
# 新增 engine/intelligence/got.py
class GraphOfThoughts:
    def __init__(self, entailment_graph):
        self.graph = entailment_graph  # 已有EntailmentGraph
        self.thoughts = {}  # node_id → LLM推理结果

    def reason_on_node(self, node_id):
        """对图中一个节点做LLM推理"""
        parents = self.graph.reverse[node_id]  # 该节点的前提
        children = self.graph.edges[node_id]   # 该节点的推论

        parent_thoughts = {p: self.thoughts.get(p, "") for p in parents}
        prompt = f"前提节点的分析: {parent_thoughts}\n请分析节点{node_id}的逻辑一致性"

        self.thoughts[node_id] = self.llm._call(prompt)
        return self.thoughts[node_id]

    def merge_paths(self, node_ids):
        """合并多条推理路径到一个结论"""
        all_thoughts = [self.thoughts[n] for n in node_ids if n in self.thoughts]
        prompt = f"综合以下{n}条推理路径:\n" + "\n".join(all_thoughts)
        return self.llm._call(prompt)

    def traverse_and_reason(self, start_nodes, merge_nodes):
        """图游走推理: 从叶子→根, 在合并点综合"""
        # 拓扑排序(已有)
        order = self.graph.topological_order()
        for node in order:
            if node in merge_nodes:
                # 合并点: 综合所有输入路径
                inputs = self.graph.reverse[node]
                self.thoughts[node] = self.merge_paths(inputs)
            else:
                # 普通节点: 单节点推理
                self.reason_on_node(node)
        return self.thoughts
```

**引导LLM使用GoT的提示词**:
```
你正在一个有向无环图上做推理。图的节点是事实和推论, 边是derives_from关系。

当前节点: {node}
前提节点(已完成分析): {parents}
后续节点(依赖你): {children}

请基于前提节点的分析, 对当前节点给出你的推理。如果多个前提节点指向不同方向, 请明确指
出并在合并时给出综合判断。
```

### 2.4 价值评估

| 场景 | 无GoT | 有GoT |
|------|-------|-------|
| 矛盾检测 | 词对匹配 | LLM在图合并点检测逻辑冲突 |
| 多推论综合 | 独立分析每条 | LLM在共享前提的合并点综合 |
| 影响传播 | 拓扑计数 | LLM标注"关键瓶颈节点" |

---

## 三、ToT (Tree of Thoughts) — 树思维

### 3.1 方法本质

```
根节点(问题) → 分支1 → 子分支1.1 → 叶(评分)
             → 分支2 → 子分支2.1 → 叶(评分)
             → 分支3 → (剪枝, 不继续)

每层: 生成N个候选 → 评估 → 保留Top-K → 继续
```

### 3.2 OntoDerive现有架构匹配度: 7/10 ⭐

OntoDerive没有原生树结构, 但推论体系天然形成推理树:

```
已有结构利用:
  推论文件中的 "结论: ..." 可以作为候选分支
  贝叶斯置信度可以作为评分函数
  矛盾检测可以作为剪枝依据
```

### 3.3 接入方案

```python
# 新增 engine/intelligence/tot.py
class TreeOfThoughts:
    def __init__(self, enhancer, scorer=None):
        self.llm = enhancer
        self.scorer = scorer or self._confidence_scorer

    def explore(self, question, facts_context, branching=3, depth=2):
        """ToT主循环: 每层生成N个候选, 保留Top-K"""
        root = {"thought": question, "children": [], "score": 1.0}
        current_level = [root]

        for d in range(depth):
            next_level = []
            for node in current_level:
                candidates = self._generate_candidates(node["thought"], facts_context, branching)
                for c in candidates:
                    score = self.scorer(c, facts_context)
                    child = {"thought": c, "children": [], "score": score}
                    node["children"].append(child)
                    next_level.append(child)
            # 保留Top-K
            next_level.sort(key=lambda x: -x["score"])
            current_level = next_level[:branching]
        return root

    def _generate_candidates(self, question, context, n):
        """LLM生成N个候选推理方向"""
        prompt = f"问题: {question}\n上下文: {context}\n生成{n}个不同的推理方向, 每条一行"
        result = self.llm._call(prompt, temperature=0.5)
        return [l.strip("- ") for l in result.split("\n") if l.strip()][:n]

    def _confidence_scorer(self, thought, context):
        """使用贝叶斯置信度作为评分(可用已有数据)"""
        prompt = f"评估这个推理方向的质量(1-10): {thought}\n上下文: {context}"
        result = self.llm._call(prompt, "只输出数字。", 0.1)
        try:
            return int(result.strip()) / 10.0
        except:
            return 0.5
```

### 3.4 价值评估

| 场景 | 无ToT | 有ToT |
|------|-------|-------|
| 策略选择 | 单一路径 | 多条路径比较后选最优 |
| 矛盾检测 | 二元判断 | 探索双方推理链后综合 |
| 推导深度 | 固定 | 按分支评估动态调整深度 |

---

## 四、Multi-Agent Debate — 多智能体辩论

### 4.1 方法本质

```
Agent A: 提出观点 + 论证
Agent B: 反驳 + 提出反证
Agent C: 仲裁 + 综合
最终: 三方达成共识或明确分歧点
```

### 4.2 OntoDerive现有架构匹配度: 8/10 ⭐⭐

OntoDerive已有的基础设施完美支持:

```
已有角色模板:
  PromptTemplate 系统 = Agent角色定义
  DOMAIN_PRESETS = 不同视角(政策/商业/学术/技术)
  矛盾检测词对 = 辩论议题

可定义角色:
  辩护方: 使用 business 领域预设, 论证推论正确
  质疑方: 使用 academic 领域预设, 寻找逻辑漏洞
  仲裁方: 使用 general 预设, 综合双方论点
```

### 4.3 接入方案

```python
# 新增 engine/intelligence/debate.py
class MultiAgentDebate:
    ROLES = {
        "defender": "你是推论的支持者。你的任务是论证为什么这些推论是正确的。",
        "challenger": "你是推论的质疑者。你的任务是从逻辑、证据、可证伪性角度找出问题。",
        "arbitrator": "你是仲裁者。你的任务是综合双方论点, 给出最终判断。",
    }

    def __init__(self, enhancer):
        self.llm = enhancer

    def debate(self, topic, context, rounds=2):
        """多轮辩论"""
        transcript = []

        # 开局: 辩护方提出论点
        defender_view = self._role_call("defender", f"请论证: {topic}", context)
        transcript.append({"role": "defender", "content": defender_view})

        for r in range(rounds):
            # 质疑方反驳
            challenge = self._role_call("challenger",
                f"对方的观点: {defender_view}\n请找出逻辑漏洞",
                context)
            transcript.append({"role": "challenger", "content": challenge})

            # 辩护方回应
            defender_view = self._role_call("defender",
                f"质疑: {challenge}\n请回应质疑并强化你的论证",
                context)
            transcript.append({"role": "defender", "content": defender_view})

        # 仲裁
        verdict = self._role_call("arbitrator",
            f"辩论记录: {transcript}\n请给出最终判断",
            context)
        transcript.append({"role": "arbitrator", "content": verdict})

        return transcript

    def _role_call(self, role, prompt, context):
        system = self.ROLES[role]
        full = f"{system}\n\n{context}\n\n{prompt}"
        return self.llm._call(full)
```

### 4.4 价值评估

| 场景 | 无辩论 | 有辩论 |
|------|--------|--------|
| 矛盾检测 | 二元判断 | 双方充分辩论后发现深层矛盾 |
| 质量评估 | 单人评分 | 质疑方挖出盲点后仲裁 |
| 策略决策 | 单视角 | 三角测量: 支持/反对/综合 |

---

## 五、综合接入路线图

```
当前架构已具备的基础:
  ✅ EntailmentGraph (图结构 — GoT天然基础)
  ✅ PromptTemplate + DOMAIN_PRESETS (角色 — Debate基础)
  ✅ BayesianNetwork (置信度 — ToT评分函数)
  ✅ 7个Action原语 (Read/Check/Trace/... — ReAct基础)

接入优先级:
  Phase A (本周): GoT — 与蕴含图天然契合, 最低开发成本
  Phase B (下周): ReAct — 已有完整Action系统, 连上即可用
  Phase C (两周): ToT + Debate — 更多探索/更深分析

最小可行接入(MVP):
  engine/intelligence/
    ├── got.py      ← GoT引擎 (基于logic.py的EntailmentGraph)
    ├── react.py    ← ReAct引擎 (基于7个已有Action)
    ├── debate.py   ← 多智能体辩论 (基于prompts.py的角色预设)
    └── tot.py      ← ToT引擎 (基于bayesian.py的置信度评分)
```

### 每个方法的引导关键词

```
ReAct: "你可以使用以下工具来验证你的推理"
GoT:   "你正在一个有向无环图上做推理, 注意合并点的综合判断"
ToT:   "探索多个推理方向, 评估后选择最优路径继续"
Debate: "从正方、反方、仲裁三个视角分析这个问题"
```
