# OntoDerive v3.6 四向升级计划

> 执行顺序: 1→3→2→4

## 1. RuleLoader 真正执行

- RuleReasoner.derive()末尾调用to_conclusion()
- 23条YAML规则不再只是加载, 产生产出
- 文件: engine/reasoners/reasoner.py

## 3. A10-A12 新模式

- A10 因果链 / A11 情景规划 / A12 权力地图
- 文件: engine/theories/analytics.py

## 2. 文档提取增强

- formalize.py 正则16→26+
- 覆盖政府公文/财报/专利/政策
- 文件: engine/formalize.py

## 4. 加权影响传播

- bayesian.py 加what-if重算
- recompute_if_changed()→Delta
- 文件: engine/theories/bayesian.py

## 验证: 197+ tests
