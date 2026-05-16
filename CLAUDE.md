# OntoDerive — 渊衍框架

> 事实驱动的一体化知识工程与方案推导框架。
> 核心推导链：事实 → 本体 → 推论 → 方案（双向可追溯）

---

## 对 agent 的标准操作流程

当你被加载到此项目时，按以下顺序执行：

### Step 1: 理解项目状态

```bash
python3 engine/derive.py --project . --check
# 如果项目未初始化，先 --init new-project
```

### Step 2: 阅读四阶段方法论

依次读取：
1. `framework/01-元模型/00-元模型定义.md` — 理解8元类型和元关系矩阵
2. `examples/z-park/README.md` — 通过示例理解完整流程
3. 检查当前项目的 `facts/`、`entities/`、`inferences/`、`scheme/` 目录

### Step 3: 执行推导引擎

```bash
# 正向推导
python3 engine/derive.py --project . --derive

# 规约检查
python3 engine/derive.py --project . --check

# 多轮迭代(每轮检查+报告)
python3 engine/derive.py --project . --rounds 3
```

### Step 4: 根据规约结果修复缺口

引擎会输出每项检查的通过/失败状态和修复建议。按优先级处理：
- BLOCKER → 立即修复
- ERROR → 本轮修复
- WARN → 记录并在后续迭代中处理

---

## 核心约束

1. **事实先于推论**：没有事实编号的推论不采用
2. **可证伪**：每个关键判断必须附带退出条件
3. **正交分解**：维度之间互不重叠
4. **双向闭环**：正向推导+反向校验=完整

---

## 健壮性评估

| 维度 | 当前状态 | 说明 |
|------|---------|------|
| 元模型 | ✅ 完备 | 8元类型×4元关系×4元约束，自指闭环 |
| 示例 | ✅ 可运行 | z-park示例4/4检查通过 |
| 引擎 | ⚠️ 覆盖4/19规约 | 基础检查完成，领域规约需按需补充 |
| 插件化 | ❌ 未打包 | 需用 create-cowork-plugin 打包 |
| MCP服务 | ❌ 未实现 | agent调用需手动执行脚本 |
| 模板系统 | ⚠️ 基础 | --init 创建最小骨架 |
| 文档生成 | ⚠️ 仅markdown | docx/pdf生成需扩展 |
