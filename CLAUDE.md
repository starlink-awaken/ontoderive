# OntoDerive — 渊衍框架 v3.0

> 事实驱动的一体化知识工程与方案推导框架。
> 核心推导链：ToolForge匹配 → 事实基座 → 类型校验 → 推论体系 → 方案产出（双向可追溯）

---

## 快速开始

```bash
# 运行检查
python3 engine/derive.py --project . --check

# 带工具匹配的完整分析
python3 engine/derive.py --project . --with-tools --goal "分析XX" --derive --check

# 运行测试
python3 -m pytest tests/ -v
```

## 项目状态 (v3.0)

| 指标 | 数值 |
|------|------|
| 引擎模块 | 16个 + 4子包(ontolang/ecosystem/toolforge/typesystem) |
| 测试数 | 114个，全部通过 |
| 核心引擎 | derive.py 147行（从540行削减73%） |
| 规约检查 | 13条(C-01~C-13)，独立模块 check.py |

## 架构概览

```
engine/
├── derive.py        核心推导引擎 (147行，check委托给check.py)
├── check.py         13条规约检查引擎 (270行)
├── pipeline.py      六阶段管道 (ToolForge→Load→Derive→Check→Resolve→Report)
├── typesystem.py    10元类型校验器
├── bayesian.py      DAG信念传播 + 环检测 + DOT可视化
├── metrics.py       KQI知识质量指数 + 历史追踪
├── controller.py    PID反馈控制 + 收敛检测
├── turing_k.py      知识状态机 + Delta + 停机检测
├── logic.py         蕴含图分析
├── ontolang/        递归下降解析器 (5文件)
├── toolforge/       TF-IDF + keyword + hybrid 三模式工具匹配
├── ecosystem/       Minerva/Sophia/Agora/eCOS适配器
├── protocols.py     生态接口契约 (ABC)
├── config.py        配置合并链
├── models.py        7个dataclass
├── constants.py     共享常量和预编译正则
├── utils.py         共享工具函数
└── mcp_server.py    统一MCP入口 (11工具)
```

## 生态接口

| 接口 | 说明 |
|------|------|
| CLI | `python3 engine/derive.py --init/--derive/--check/--rounds/--goal/--with-tools` |
| MCP | 11工具：ontoderive_init/derive/check/rounds/generate/analyze/config/delta + toolforge_match/select/guide |
| Python | `from engine.derive import OntoDerive; od = OntoDerive('my-project'); od.derive(); od.check()` |
| Pipeline | `from engine.pipeline import DerivePipeline; pipe = DerivePipeline('my-project'); pipe.run()` |
