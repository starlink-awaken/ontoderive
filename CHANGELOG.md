# Changelog

## v3.0.0 (2026-05-19) — LLM增强 + 架构成熟

### 新增
- LLM增强层: engine/llm.py — 零依赖降级 + ollama/openai/anthropic自动检测
- 自动检测本地qwen3.5:4b等模型
- derive()推导提示支持LLM深度洞察
- test_llm.py (6测试)

### 架构
- Strategy Pattern解耦: check_theory.py — C-09~C-13注册表
- check.py 270→219行
- 每个理论模块独立check_xxx()函数
- OntoDerive(DeriveInterface) + ToolForge(ToolForgeInterface) ABC契约

### 能力
- INF-to-INF多层推导链 + 置信度传播
- 矛盾检测30+词对 + 否定模式 + 强度分级
- 中文bigram TF-IDF (0→5结果)
- 置信度基于来源差异化
- 7元TypeValidator, C-07纯TypeValidator
- 推导链增强: DAG深度 + 循环检测 + 矛盾标记

### 测试与CI
- 156测试 (E2E + 集成 + 单元)
- GitHub Actions: Python 3.9/3.11/3.12

### 文档
- docs/ARCHITECTURE.md (264行)
- docs/USER_GUIDE.md (193行)
- framework实现状态附录

---

## v2.0.0 — 工程基座重构
- 测试 0→67
- utils/models共享基础设施
- Pipeline六阶段管道
- ToolForge TF-IDF三模式
- Bayesian DAG + 环检测
- 递归下降OntoLang解析器
- 统一MCP 11工具

---

## v1.0.0 — 初始版本
- 7引擎模块, 4正则, 0测试
