# AGENTS.md — OntoDerive

> AI Agent 入口。详见 `CLAUDE.md` 完整文档。

## 快速导航

| 命令 | 用途 |
|------|------|
| `python3 engine/cli.py derive --project <path> --check` | 知识推导检查 |
| `python3 engine/cli.py pipeline --text "<text>"` | 四阶段形式化推理 |
| `python3 -m pytest tests/ -q` | 跑测试 (197 tests) |

## 关键文件

| 文件 | 用途 |
|------|------|
| `engine/derive.py` | 核心推导引擎 |
| `engine/pipeline_v4.py` | 四阶段正式推理管线 |
| `engine/reasoners/` | 推理器 (19条规则R1-R19) |
| `engine/toolforge/` | 73 工具匹配 |
| `engine/mcp_server.py` | 11 工具 MCP Server |

## 版本

v3.6.4 · 57 模块 · 9 分析模式 · 5 层架构

详见 `CLAUDE.md`
