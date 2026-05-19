# OntoDerive v2.1 — 硬骨头冲刺

## Context

Phase 0-4完成，审计评分≈5.9/10。五个硬骨头待攻坚：
1. derive()不做推导（只做正则计数）
2. MOF四层无代码（只在文档中）
3. 六论数据流断裂（通过文件系统通信，各自重新实例化）
4. 测试缺口大（Pipeline/生态/MCP零测试）
5. 文档与代码脱节

ISA文件：`MEMORY/WORK/ontoderive-v21/ISA.md`（12条ISC，10个Feature，E3级）

## 已完成

- [x] F8: ToolForge默认keyword模式
- [x] F4: PID历史通配读取 + check结果时间戳存储

## 待执行

### Wave 1（并行，1天）：F1 + F2 + F9

| Feature | 文件 | 说明 |
|---------|------|------|
| **F1** derive升级 | `engine/derive.py` | derive()输出confidence_distribution和chain_depth，集成贝叶斯/KQI/PID结果 |
| **F2** 类型系统 | `engine/typesystem.py` 新增 | 10元类型校验器，ID前缀与声明类型一致性检查 |
| **F9** 文档标注 | `framework/02-迭代方案-v2.md` | 逐条标注✅/⚠️/❌实现状态 |

### Wave 2（1天）：F3

| Feature | 文件 | 说明 |
|---------|------|------|
| **F3** 六论管道 | `engine/pipeline.py`, `engine/bayesian.py`, `engine/metrics.py` | Pipeline内存传递；Bayesian暴露get_distribution()供Metrics消费；消除重复扫描 |

### Wave 3（并行，1.5天）：F5 + F6 + F7

| Feature | 文件 | 说明 |
|---------|------|------|
| **F5** Pipeline测试 | `tests/test_pipeline.py` 新增 | 端到端流程 |
| **F6** 生态测试 | `tests/test_ecosystem.py` 新增 | Minerva/Sophia/Agora/eCOS |
| **F7** MCP测试 | `tests/test_mcp_server.py` 新增 | 11工具响应格式 |

### Wave 4（1天）：F10

| Feature | 文件 | 说明 |
|---------|------|------|
| **F10** 补全测试 | `tests/test_cli.py`, `tests/test_config.py`, `tests/test_watcher.py` 新增 | 总测试数≥100 |

## 验收

```bash
python3 -m pytest tests/ -q  # ≥100 passed
```

全部12条ISC通过，详见ISA.md的Verification部分。
