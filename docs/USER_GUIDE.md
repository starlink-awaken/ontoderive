# OntoDerive 用户指南

> 面向人类用户的完整使用说明

---

## 安装

```bash
# 方式一：pip安装
pip install ontoderive

# 方式二：源码运行
git clone https://github.com/your-org/ontoderive.git
cd ontoderive
export PYTHONPATH=$PYTHONPATH:$(pwd)/engine
```

## 核心概念

| 概念 | 说明 | 类比 |
|------|------|------|
| 事实基座(facts/) | 可验证的数据+政策 | 案件的证据 |
| 实体(entities/) | 关键角色+组织+项目 | 案件的角色 |
| 推论(inferences/) | 基于事实的逻辑推导 | 律师的论证 |
| 方案(scheme/) | 最终产出文档 | 判决书 |
| 规约检查(check) | 验证方案的完整性 | 二审审查 |

## 完整工作流

### 第一步：初始化

```bash
python3 engine/derive.py --init my-analysis
cd my-analysis
```

### 第二步：填充事实

编辑 `facts/data.md`：

```markdown
| 编号 | 数据 | 数值 | 来源 |
|------|------|------|------|
| D-F1 | 总用户数 | 100万 | 2026年报 |
| D-F2 | 月活用户 | 30万 | 产品月报 |
```

编辑 `facts/policy.md`（可选）：

```markdown
| 编号 | 政策 | 发布主体 | 日期 |
|------|------|---------|------|
| P-F1 | 数据安全法 | 全国人大 | 2021 |
```

### 第三步：定义实体

编辑 `entities/actors.md`：

```markdown
| 实体 | 类型 | 角色 | 数量 |
|------|------|------|------|
| ORG-XX公司 | 组织 | 运营主体 | 1 |
| ROL-普通用户 | 角色 | 使用者 | 100万(D-F1) |
```

### 第四步：建立推论

编辑 `inferences/analysis.md`：

```markdown
## INF-L1：活跃度不足

推导过程：
1. 总用户100万(D-F1)但月活仅30万(D-F2)
2. 活跃率30%，低于行业均值50%
3. 推论：产品留存存在问题
- derives_from: [D-F1, D-F2]
```

### 第五步：编写方案

编辑 `scheme/report.md`：

```markdown
# XX产品分析报告

## 核心发现
月活率30%(D-F1/D-F2)，存在留存问题(INF-L1)
```

### 第六步：执行验证

```bash
python3 ../engine/derive.py --project . --derive --check
python3 ../engine/derive.py --project . --rounds 3
python3 ../engine/derive.py --project . --generate report
cat _derivation_logs/report.md
```

## CLI 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `--init NAME` | 初始化新项目 | `--init my-project` |
| `--project PATH` | 指定项目路径 | `--project .` |
| `--derive` | 正向推导 | `--derive` |
| `--check` | 规约检查 | `--check` |
| `--resolve` | 自动修复 | `--resolve` |
| `--rounds N` | 多轮迭代 | `--rounds 5` |
| `--generate report` | 生成报告 | `--generate report` |

## 8条规约速查

| 编号 | 检查项 | 严重度 | 触发条件 |
|------|-------|--------|---------|
| C-01 | 事实基座完整性 | BLOCKER | facts/目录不存在 |
| C-02 | 推论体系完整性 | ERROR | inferences/目录不存在 |
| C-03 | 方案文件完整性 | ERROR | scheme/目录无文件 |
| C-04 | 事实可追溯性 | WARN | 事实编号在方案中未被引用 |
| C-05 | 断言可追溯性 | WARN | 断言无编号引用(<30%) |
| C-06 | 可证伪性 | WARN | 核心预测无条件句(<15%) |
| C-07 | ID合规性 | WARN | 非标准实体ID |
| C-08 | 引擎健康度 | BLOCKER | derive.py不可运行 |
