---
name: ontoderive
description: >
  OntoDerive 渊衍框架——事实驱动的一体化知识工程与方案推导。
  从"事实→本体→推论→方案"的全链路可追溯推导。
  支持元建模、正向推导、反向规约校验、多轮迭代收敛。
triggers:
  - "渊衍框架"
  - "ontoderive"
  - "事实驱动推导"
  - "从事实到方案"
  - "知识工程框架"
  - "元建模"
---

# OntoDerive Skill — 渊衍框架执行指引

> 本skill是OntoDerive方法论的操作手册。当需要从零开始构建一个"事实→方案"的知识工程时使用。

## 加载后的标准动作

1. **读 CLAUDE.md** — 了解项目结构和核心推导链
2. **读 framework/01-元模型/00-元模型定义.md** — 理解元类型系统
3. **检查项目状态** — 查看 facts/, entities/, inferences/, scheme/ 目录
4. **执行推导引擎** — `python3 engine/derive.py --derive`
5. **执行规约检查** — `python3 engine/derive.py --check`

## 四阶段工作流

### 阶段一：事实基座建设
- 创建 facts/data.md（数据事实表）
- 创建 facts/policy.md（政策事实表）  
- 每项事实标注来源和编号(D-Fx/P-Fx)

### 阶段二：实体本体建模
- 创建 entities/organizations.md（组织实体）
- 创建 entities/roles.md（角色实体）
- 创建 entities/projects.md（项目实体）
- 每项实体标注ID(ORG-x/ROL-x/PRJ-x)和核心属性

### 阶段三：推论体系建立
- 创建 inferences/contradictions.md（矛盾诊断）
- 创建 inferences/derivations.md（业务/架构推导）
- 每条推论标注 derives_from 事实编号

### 阶段四：方案产出与校验
- 编写 scheme/ 下的方案文档
- 对每项断言添加来源编号引用
- 运行 `--rounds 3` 迭代收敛

## 核心纪律

1. 事实先于推论——没有事实基座不得开始推论
2. 可追溯——每个断言必须有来源编号
3. 可证伪——每个关键判断附带退出条件
4. 正交分解——维度之间不重叠

## 与推导引擎的协作

```bash
# 引擎在 engine/derive.py
python3 engine/derive.py --init my-project  # 初始化
python3 engine/derive.py --project . --derive --check  # 推导+检查
python3 engine/derive.py --project . --rounds 5  # 5轮迭代
```
