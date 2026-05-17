"""
OntoDerive 形式语言层 — OntoLang解析器
=========================================
BNF语法解析器，支持entity/fact/inference/protocol四种声明语句。
基于正则表达式实现，无需额外依赖。

BNF:
    EntityDef  ::= "entity" ID ":" Type "{" Property* "}"
    FactDef    ::= "fact" ID ":" Type "{" value: NUM, source: STR "}"
    Inference  ::= "inference" ID ":" Type "{" derives_from: [ID*], conclusion: STR "}"
    Protocol   ::= "protocol" ID ":" Type "{" constraint: STR "}"

用法:
    from engine.ontolang import OntoLangParser
    parser = OntoLangParser()
    ast = parser.parse(source)
"""
import re

class OntoLangParser:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def parse(self, source):
        """解析OntoLang源文本，返回AST"""
        ast = {"entities": [], "facts": [], "inferences": [], "protocols": [], "errors": []}
        self.errors = []
        self.warnings = []

        lines = source.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):  # 注释
                continue

            # Entity: entity ORG-xxx : Organization { ... }
            m = re.match(r'^entity\s+(ORG-\w+|ROL-\w+|PRJ-\w+)\s*:\s*(\w+)', stripped)
            if m:
                ast["entities"].append({
                    "id": m.group(1), "type": m.group(2), "line": i,
                    "raw": stripped
                })
                continue

            # Fact: fact D-F1 : DataPoint { value: 100, source: "xxx" }
            m = re.match(r'^fact\s+(D-F\d+|P-F\d+)\s*:\s*(\w+)', stripped)
            if m:
                ast["facts"].append({
                    "id": m.group(1), "type": m.group(2), "line": i,
                    "raw": stripped
                })
                continue

            # Inference: inference INF-L1 : Contradiction { derives_from: [...], conclusion: "..." }
            m = re.match(r'^inference\s+(INF-[\w-]+)\s*:\s*(\w+)', stripped)
            if m:
                ast["inferences"].append({
                    "id": m.group(1), "type": m.group(2), "line": i,
                    "raw": stripped
                })
                continue

            # Protocol: protocol P-xxx : Constraint { constraint: "..." }
            m = re.match(r'^protocol\s+(P-[\w-]+)\s*:\s*(\w+)', stripped)
            if m:
                ast["protocols"].append({
                    "id": m.group(1), "type": m.group(2), "line": i,
                    "raw": stripped
                })
                continue

        return ast

    def validate(self, ast):
        """验证AST的语义正确性"""
        errors = []

        # 检查实体ID是否使用标准前缀
        for e in ast.get("entities", []):
            prefix = e["id"].split("-")[0]
            valid_prefixes = ["ORG", "ROL", "PRJ"]
            if prefix not in valid_prefixes:
                errors.append(f"E{e['line']}: '{e['id']}' 前缀无效, 应为 {valid_prefixes}")

        # 检查推论是否有 derives_from
        for inf in ast.get("inferences", []):
            if "derives_from" not in inf.get("raw", ""):
                errors.append(f"E{inf['line']}: '{inf['id']}' 缺少derives_from声明")

        # 检查事实ID命名
        for f in ast.get("facts", []):
            if not re.match(r'^(D-F|P-F)\d+', f["id"]):
                errors.append(f"E{f['line']}: '{f['id']}' 事实ID格式无效")

        return errors

    def test_suite(self):
        """内置测试用例"""
        test_source = """-- 实体定义
entity ORG-国转中心 : Organization { governance: "双轨制" }
entity ROL-技术经理人 : Role { count: 133 }

-- 事实声明
fact D-F1 : DataPoint { value: 470, source: "中心介绍PDF" }
fact P-F9 : Policy { authority: "北京市" }

-- 推论
inference INF-L1 : Contradiction { derives_from: [D-F1], conclusion: "需要双轨分离" }

-- 规约
protocol P-CROSS-001 : Constraint { constraint: "mapping_coverage >= 90%" }
"""
        return self.parse(test_source)
