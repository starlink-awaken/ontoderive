# OntoDerive 架构收敛与产品化计划 (P0-P4)

## Context

研究发现了六个结构性问题:
1. 三套推理系统并存互不协作
2. v4.0管线是孤岛代码未集成
3. 版本号与文档严重漂移(README v3.1, ARCHITECTURE v2.2, ROADMAP v1.2)
4. 架构文档与实际代码结构不符
5. watcher/extractor已实现但CLI无入口
6. MCP server未暴露pipeline_v4

## 阶段规划

### P0: 止血与对齐 (1h)
- 统一版本号: README(v3.1→3.2), cli.py(v2.0→3.2)
- 更新ARCHITECTURE.md反映v3.x架构
- 废弃ROADMAP.md为ARCHIVED
- 更新CLAUDE.md反映真实模块数

### P1: 推理引擎统一 (2h)
- RuleReasoner + FormalReasoner → UnifiedReasoner
- 统一输出格式: certainty标注 + derives_from
- 确定性/启发式/结构性三层分类

### P2: v4.0管线集成 (1h)  
- pipeline_v4集成到derive()作为formal模式
- CLI新增 formal 命令

### P3: 接口补齐与文档 (1h)
- watcher/extractor CLI入口
- MCP server扩展pipeline_v4

### P4: 架构简化 + 生态闭环 (1h)
- 子包收敛
- 版本最终统一至3.3.0

## 验收
- 162+ tests passed
- 所有版本号一致
- CLI help文本正确
- 真实文档测试可运行
