# OntoDerive v3.5 — 使用指南

> 知识工程分析平台。197 tests, 9分析模式, 5格式导出。五分钟上手。

---

## 一、安装

```bash
git clone https://github.com/starlink-awaken/ontoderive.git && cd ontoderive
python3 -m pytest tests/ -q   # 期望: 197 passed
```

---

## 二、快速体验

```bash
# 内置案例: z-park (中关村科学城)
python3 engine/cli.py derive --project examples/z-park
# 输出: 事实+推论+推导结论, 含分析模式洞察

# HTML报告导出
python3 engine/cli.py generate --project examples/z-park --export html
# 输出: export.html (浏览器可打开)

# 本体映射导出
python3 engine/cli.py generate --project examples/z-park --export jsonld
# 输出: export.json (schema.org + PROV-O格式)
```

---

## 三、核心能力

### CLI (9子命令 + 4导出格式)
```bash
python3 engine/cli.py init my-analysis            # 初始化项目
python3 engine/cli.py derive --project my-analysis  # 结构分析
python3 engine/cli.py check --project my-analysis   # 规约检查
```

### Python API
```python
from engine.derive import OntoDerive
od = OntoDerive("my-project")
s = od.derive()
# s["derived_conclusions"] → 推导结论
# s["derivation_hints"]    → 结构提示
# s["confidence_distribution"] → 置信度分布
results = od.check()
```

### Pipeline
```python
from engine.pipeline import DerivePipeline
pipe = DerivePipeline("my-project")
pipe.set_goal("分析目标")
pipe.run()
```

### MCP (11工具)
```bash
python3 engine/mcp_server.py
# ontoderive_init/derive/check/rounds/generate/analyze/config/delta
# toolforge_match/select/guide
```

---

## 四、LLM增强（可选）

```bash
# 本地35B模型
ONTODERIVE_LLM_BACKEND=local \
ONTODERIVE_LLM_MODEL=qwopus3.6-35b-a3b-v1 \
python3 engine/cli.py analyze --project examples/demo-product

# ollama
ONTODERIVE_LLM_BACKEND=ollama python3 engine/cli.py analyze --project ...
```

---

## 五、项目结构

```
my-analysis/
├── facts/
│   ├── data.md       ← 数据事实 (| D-F1 | 描述 | 数值 | 来源 |)
│   └── policy.md     ← 政策事实 (| P-F1 | 政策 | 发布主体 | 日期 |)
├── entities/          ← 实体 (ORG-/ROL-/PRJ-)
├── inferences/        ← 推论 (## INF-标题, derives_from: [...])
├── scheme/            ← 方案产出
└── _derivation_logs/  ← 运行日志(自动生成)
```

### ID约定

| 元素 | 格式 | 示例 |
|------|------|------|
| 数据事实 | D-F数字 | D-F1 |
| 政策事实 | P-F数字 | P-F9 |
| 推论 | INF-xxx | INF-L1 |

---

## 六、工具推荐

```python
from engine.toolforge.matcher import ToolForge
tf = ToolForge()
for t in tf.select("分析产品策略"):
    print(f"{t['id']} {t['name']} {t['score']}")
```

---

## 七、案例运行

```bash
# 案例1: 产品策略分析
python3 engine/cli.py derive --project examples/demo-product --check

# 案例2: 中关村科学城
python3 engine/cli.py derive --project examples/z-park --check

# 案例3: 贝叶斯演示
python3 engine/cli.py derive --project examples/bayesian-demo
```

---

## 八、测试

```bash
python3 -m pytest tests/ -v              # 全量156
python3 -m pytest tests/test_derive.py   # 单模块
```
