# OntoDerive Agent Guide v3.5

> AI Agent标准操作流程。57模块, 197 tests, 9分析模式。

## 标准操作流程 (SOP)

### Step 1: 项目诊断

```python
# 检查项目状态
python3 engine/cli.py check --project .
# 期望: 197 tests passed

# 读取关键文件
# - CLAUDE.md: 项目入口+架构速览
# - docs/AGENTS.md: Agent能力清单
# - README.md: 项目概述
# - CHANGELOG.md: v3.1→v3.5 完整记录
# - facts/data.md: 事实基座
# - entities/*.md: 实体定义
# - inferences/*.md: 推论体系
# - scheme/*.md: 方案文件
```

### Step 2: 理解四阶段方法论

依次读取以下文件理解框架：

1. `framework/01-元模型/00-元模型定义.md` — 10元类型+4元关系
2. `examples/z-park/README.md` — 完整示例
3. `ns/NAMESPACE.md` — 命名空间规范

### Step 3: 执行推导

```bash
# 正向推导: 统计事实/实体/推论
python3 engine/derive.py --project . --derive

# 规约检查: 8条规约
python3 engine/derive.py --project . --check

# 多轮迭代: 推导→检查→报告
python3 engine/derive.py --project . --rounds 3
```

### Step 4: 根据结果修复

check的输出格式：

```
✅ [PASS] C-01 — 事实文件: 2 个
🟡 [WARN] C-05 — 断言4个, 可追溯1个, 追溯率25%
  → 🔧 在含'应该/必须/需要'的句子旁标注事实编号引用
🔴 [ERROR] C-02 — 推论文件: 0 个
  → 🔧 创建 inferences/contradictions.md
```

你应按照 **BLOCKER → ERROR → WARN** 的顺序处理：

| 优先级 | 动作 |
|--------|------|
| BLOCKER | 立即修复，不修复无法继续 |
| ERROR | 本轮修复，影响方案完整性 |
| WARN | 记录并在后续迭代中处理 |

### Step 5: 生成方案

```bash
python3 engine/derive.py --project . --generate report
```

## MCP接口

如果MCP server已启动，agent可以直接调用工具：

```json
{
  "tool": "ontoderive_check",
  "arguments": {"project": "/path/to/project"}
}
```

可用工具：
- `ontoderive_init(name)` — 初始化新项目
- `ontoderive_derive(project)` — 正向推导
- `ontoderive_check(project)` — 规约检查
- `ontoderive_rounds(project, rounds)` — 多轮迭代

## 命名空间规范

所有实体ID必须遵循：

```
od:{domain}:{type}-{name}
示例: od:analysis:INF-L1, od:analysis:D-F1
```

## 核心约束

1. **事实先于推论**：没有事实编号的推论不被采用
2. **可证伪**：每个关键判断必须附带退出条件
3. **正交分解**：维度之间互不重叠
4. **双向闭环**：正向推导+反向校验=完整
