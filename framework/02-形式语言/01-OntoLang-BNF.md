# 形式语言层——OntoLang BNF解析器

> 实现位置: engine/ontolang.py | 集成规约: C-13

## BNF语法

```
EntityDef  ::= "entity" ID ":" Type "{" Property* "}"
FactDef    ::= "fact" ID ":" Type "{" Value "}"
Inference  ::= "inference" ID ":" Type "{" derives_from "}"
Protocol   ::= "protocol" ID ":" Type "{" constraint "}"
```

## 示例

```ontolang
entity ORG-国转中心 : Organization { governance: "双轨制" }
fact D-F1 : DataPoint { value: 470, source: "中心介绍PDF" }
inference INF-L1 : Contradiction { derives_from: [D-F1] }
```

## 验证

```bash
python3 engine/derive.py --check  # C-13 AST节点6个,错误0个
```
