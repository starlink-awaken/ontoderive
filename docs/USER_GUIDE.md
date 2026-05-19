# OntoDerive v2.2 — 使用指南

> 从零开始，五分钟掌握 OntoDerive

---

## 一、安装

```bash
git clone https://github.com/starlink-awaken/ontoderive.git
cd ontoderive
python3 -m pytest tests/ -q   # 期望：114 passed
```

零外部依赖（Python 3.8+标准库）。

---

## 二、快速体验

```bash
# 运行内置示例
python3 engine/derive.py --project examples/z-park --check
# 输出：📊 规约检查: 13/13 通过

# 带工具匹配的完整分析
python3 engine/derive.py --project examples/z-park \
  --with-tools --goal "中关村科技园区" --derive --check
```

---

## 三、四种使用方式

### 方式1：CLI

```bash
# 初始化新项目
python3 engine/derive.py --init my-analysis

# 正向推导 + 规约检查
python3 engine/derive.py --project my-analysis --derive --check

# 多轮迭代（推导→检查→修复→重复至收敛）
python3 engine/derive.py --project my-analysis --rounds 5

# 生成报告
python3 engine/derive.py --project my-analysis --generate report
```

### 方式2：Python API

```python
from engine.derive import OntoDerive

od = OntoDerive("my-project")
summary = od.derive()
# {'facts': 10, 'inferences': 3,
#  'confidence_distribution': {'mean': 0.85, ...},
#  'entailment_graph': {'nodes': 25, 'max_depth': 3, ...}}

results = od.check()
passed = sum(1 for r in results if r["passed"])
print(f"{passed}/13 通过")
```

### 方式3：Pipeline

```python
from engine.pipeline import DerivePipeline

pipe = DerivePipeline("my-project")
pipe.set_goal("分析新能源汽车市场", "竞争格局")
pipe.run()  # 6阶段全流程：ToolForge→Load→Derive→Check→Resolve→Report
result = pipe.to_analysis_result()
```

### 方式4：MCP Server

```bash
python3 engine/mcp_server.py   # 启动stdio JSON-RPC，11工具就绪
```

工具列表：`ontoderive_init/derive/check/rounds/generate/analyze/config/delta` + `toolforge_match/select/guide`

---

## 四、项目结构

`--init my-project` 生成：

```
my-project/
├── facts/data.md       ← 数据事实 (| D-F1 | 描述 | 数值 | 来源 |)
├── facts/policy.md     ← 政策事实 (| P-F1 | 政策 | 发布主体 | 日期 |)
├── entities/actors.md  ← 实体 (**ORG-名称** : Organization)
├── inferences/analysis.md ← 推论 (## INF-L1 标题, derives_from: [D-F1])
├── scheme/report.md    ← 方案产出
└── _derivation_logs/   ← 运行日志（自动生成）
```

### ID约定

| 元素 | 格式 | 示例 |
|------|------|------|
| 数据事实 | `D-F数字` | D-F1 |
| 政策事实 | `P-F数字` | P-F9 |
| 组织 | `ORG-名称` | ORG-国转中心 |
| 角色 | `ROL-名称` | ROL-技术经理人 |
| 项目 | `PRJ-名称` | PRJ-平台建设 |
| 推论 | `INF-名称` | INF-L1 |
| 推导链 | `derives_from: [D-F1]` | 推论末尾标注 |

---

## 五、常用场景

### 5.1 市场分析

```bash
python3 engine/derive.py --goal "新能源汽车市场分析"
# 编辑 新能源汽车市场分析/facts/data.md 填入数据
python3 engine/derive.py --project 新能源汽车市场分析 \
  --with-tools --derive --check
```

### 5.2 方案编制

按四阶段：事实基座→实体本体→推论体系→方案产出，每阶段运行 `--check`，完成后 `--rounds 5` 收敛。

### 5.3 工具推荐

```python
from engine.toolforge.matcher import ToolForge
tf = ToolForge()
for t in tf.select("分析新能源汽车市场", top_n=3):
    print(f"{t['id']} {t['name']} ({t['score']})")
# S-003 先市场后技术 (3.0)
# M-001 波特五力 (2.5)
# M-005 PEST分析 (1.5)
```

### 5.4 类型校验

```python
from engine.typesystem import TypeValidator
tv = TypeValidator()
assert tv.check_id("D-F1").is_valid     # True
assert not tv.check_id("BAD-xxx").is_valid  # False
```

---

## 六、配置 (ontoderive.yaml)

```yaml
toolforge_mode: keyword     # keyword | tfidf | hybrid
toolforge_top_n: 5
check_thresholds:
  assertion_traceability: 0.30
  falsifiability: 0.15
derive_iterations: 3
```

优先级：env vars > CLI args > project yaml > defaults

---

## 七、生态集成

```python
# Minerva研究 → OntoDerive事实
from engine.ecosystem import minerva_to_facts
minerva_to_facts({"facts": [{"description":"企业数","value":"240"}]}, "my-project")

# Sophia → OntoDerive框架推荐
from engine.ecosystem import recommend_frameworks
recommend_frameworks("分析新能源汽车市场")

# eCOS事件观察
from engine.ecosystem import create_observer
obs = create_observer()
```

---

## 八、测试

```bash
python3 -m pytest tests/ -v                    # 全量 114测试
python3 -m pytest tests/ --cov=engine          # 覆盖率
python3 -m pytest tests/test_typesystem.py -v  # 单模块
```
