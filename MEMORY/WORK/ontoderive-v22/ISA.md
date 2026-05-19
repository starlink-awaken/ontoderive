# OntoDerive v2.2 — 基于图谱分析的架构瘦身

> ISA v1.0 | E3 Tier | 2026-05-18  
> 知识图谱显示：Parser 25连接枢纽化、OntoDerive 23连接上帝对象、凝聚度<0.10边界模糊、TypeValidator新模块已跻身Top10

---

## Problem

知识图谱揭示三个架构问题：

1. **上帝对象**：`OntoDerive`(derive.py) 23连接，直接依赖所有六论模块+CLI+Pipeline+MCP。任何改动都要经过它，是系统的单点瓶颈。图凝聚度仅0.05-0.10说明社区边界模糊。

2. **TypeValidator未接入**：typesystem.py已跻身Top10（18连接），但未被C-07或OntoLang语义分析使用，处于"有但没用"的状态。

3. **生态契约虚设**：`protocols.py`中`DeriveInterface`/`ToolForgeInterface`定义为`@runtime_checkable Protocol`但没有任何类显式实现它们。`isinstance(obj, DeriveInterface)`永远False。

---

## Vision

- `derive.py`从380行上帝对象拆为三个模块：`check.py`(规约检查)、`derive.py`(核心推导)、`cli.py`(入口)，各司其职
- 图凝聚度从0.05-0.10提升至0.15+
- TypeValidator成为C-07的正式后端，替代简单正则
- `OntoDerive`类显式继承`DeriveInterface`，`ToolForge`继承`ToolForgeInterface`

---

## Out of Scope

- Parser成为统一数据入口（留给v2.3）
- 测试harness/fixtures（留给v2.3）
- 六论模块统一公开接口（留给v2.3）

---

## Principles

1. **单一职责**：删除后的`derive.py`只做推导逻辑，不做规约检查、不做CLI解析
2. **契约先行**：接口定义为ABC，实现类显式继承，编译期可验证
3. **渐进替换**：TypeValidator先接入C-07，再逐步替换各处硬编码正则

---

## Constraints

- 向后兼容：CLI `python3 engine/derive.py --check --derive` 不受影响
- 测试不退：109个测试全部通过，新增测试不减少
- 零外部依赖

---

## Goal

将`OntoDerive`上帝对象拆分为职责清晰的模块，TypeValidator接入实际使用，生态接口变为可验证的ABC合约，图凝聚度提升30%。

---

## Criteria

- [ ] **ISC-1**: `derive.py`行数 ≤ 200（从380行削减）
  - Anti: derive.py超过200行

- [ ] **ISC-2**: `engine/check.py` 作为独立模块存在，`OntoDerive.check()`委托给`check.py`
  - Anti: 规约检查逻辑仍在derive.py中

- [ ] **ISC-3**: `TypeValidator.check_id()` 被C-07调用，C-07结果包含具体类型错误（不只是"异常格式N个"）

- [ ] **ISC-4**: `import protocols; isinstance(od, DeriveInterface)` 返回True
  - Anti: isinstance返回False

- [ ] **ISC-5**: `import protocols; isinstance(tf, ToolForgeInterface)` 返回True

- [ ] **ISC-6**: 109个测试全部通过，新增`test_check.py` ≥ 5个测试

- [ ] **ISC-7**: 图凝聚度中位数 ≥ 0.10（重新运行graphify AST提取验证）
  - Anti: 凝聚度中位数 < 0.10

---

## Test Strategy

| ISC | Type | Check | Threshold | Tool |
|-----|------|-------|-----------|------|
| ISC-1 | unit | wc -l engine/derive.py | assert ≤ 200 | pytest |
| ISC-2 | unit | import check; assert check.run | module exists | pytest |
| ISC-3 | unit | C-07调用TypeValidator | assert results has type_errors | pytest |
| ISC-4 | unit | isinstance(od, DeriveInterface) | assert True | pytest |
| ISC-5 | unit | isinstance(tf, ToolForgeInterface) | assert True | pytest |
| ISC-6 | unit | pytest tests/ -q | ≥ 109 + 5 new | pytest |
| ISC-7 | manual | 重新运行graphify | cohesion med ≥ 0.10 | graphify |

---

## Features

| Name | Description | Satisfies | Depends On | Parallelizable |
|------|-------------|-----------|------------|----------------|
| **F1** 拆分check.py | 从derive.py提取13条规约检查→engine/check.py；derive.py委托调用 | ISC-1, ISC-2 | — | true |
| **F2** TypeValidator接入C-07 | C-07使用TypeValidator替代简单正则，输出具体类型错误 | ISC-3 | F1 | false |
| **F3** Protocol契约具象化 | DeriveInterface→ABC；OntoDerive显式继承；ToolForge继承ToolForgeInterface | ISC-4, ISC-5 | — | true |
| **F4** 测试补充 | test_check.py + test_protocols.py + 更新test_derive.py | ISC-6 | F1, F3 | false |

### 执行顺序

```
F1(拆分check.py) + F3(Protocol契约)  →  并行，2h
F2(TypeValidator接入C-07)             →  依赖F1，1h
F4(测试补充)                           →  依赖F1+F2+F3，1h
```

---

## Verification

```bash
# ISC-1
wc -l engine/derive.py | awk '{assert $1 <= 200, "derive.py still " $1 " lines"}'

# ISC-2
python3 -c "from engine.check import run_check; print('check.py OK')"

# ISC-3
python3 engine/derive.py --project examples/z-park --check 2>&1 | grep -q "类型错误" && echo "ISC-3 OK"

# ISC-4, ISC-5
python3 -c "
from engine.derive import OntoDerive
from engine.protocols import DeriveInterface
from engine.toolforge.matcher import ToolForge
from engine.protocols import ToolForgeInterface
assert isinstance(OntoDerive('.'), DeriveInterface)
assert isinstance(ToolForge(), ToolForgeInterface)
print('ISC-4,5 OK')
"

# ISC-6
python3 -m pytest tests/ -q  # ≥ 114 passed
```
