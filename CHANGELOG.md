# Changelog

All notable changes to OntoDerive will be documented in this file.

## [2.0.0] - 2026-05-17

### Added
- **ToolForge 集成**: MindForge 思维工具匹配引擎并入 `engine/toolforge/`
- `--with-tools` 参数: 推导前自动匹配适合的思维框架
- `--tool-context` 参数: 指定匹配上下文关键词
- ToolForge MCP Server (`engine/toolforge/mcp_server.py`): 3 tools (match/select/guide)
- `to_inference_guide()`: 将匹配工具映射为 OntoDerive 推导步骤
- `select()`: 跨类别 Top-N 工具选择
- 工具目录 v2.0: 从 30 工具扩展至 53 工具
- 新增三大垂直领域: 政府治理、教育科技、产业园区
- `engine/toolforge/README.md`: ToolForge 使用文档

### Changed
- 推导链从 "事实→方案" 扩展为 "工具匹配→事实→方案"
- README 更新至 v2.0.0 统计数据和架构描述
- MANIFESTO.md §2.4 新增 ToolForge 前置匹配章节
- MindForge README 标记为已归档，指向新模块
- derive.py `--goal` 参数兼容 `--with-tools` 联动

### Fixed
- `--goal` 与 `--with-tools` 同时使用时不再触发目标驱动初始化
- 目录名称模糊匹配增加 0.5 分加权

## [1.4.0] - 2026-05-16

### Added
- 13 项规约检查 (C-01 ~ C-13)
- 贝叶斯置信度传播引擎
- KQI 知识质量指标
- PID 反馈控制器
- 知识图灵机快照/回放
- MCP Server (8 tools)
- 文件监听器 (watcher.py)
- 上下文事实提取器 (extractor.py)
- Self-verify 自举验证通过

## [1.0.0] - 2026-05-15

### Added
- 初始版本: 事实驱动推导引擎
- 8 项基础规约检查
- MOF 四层架构
- 10 元类型 + 4 元关系
- 命令行接口 (derive/check/resolve/rounds/generate)
- z-park 内置示例
