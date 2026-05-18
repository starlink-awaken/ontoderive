"""OntoLang v2 解析器包入口 — 同时导出v1兼容的 OntoLangParser"""
import re

from .ast import AST, EntityDef, FactDef, InferenceDef, ProtocolDef, RelationDef, SourcePos, ParseError, SemanticError
from .parser import Parser, Lexer
from .semantic import SemanticAnalyzer
from .codegen import to_markdown, to_json, to_legacy_ast


class OntoLangParserV2:
    def __init__(self, filename=""):
        self.filename = filename
        self.parser = Parser(filename)
        self.semantic = SemanticAnalyzer()

    def parse(self, source):
        return self.parser.parse(source)

    def validate(self, ast):
        return self.semantic.analyze(ast)

    def test_suite(self):
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
        ast = self.parse(test_source)
        errors = self.validate(ast)
        return to_legacy_ast(ast), errors, len(self.parser.errors)


# v1兼容接口 — 与旧 ontolang.OntoLangParser 保持相同api
class OntoLangParser:
    def __init__(self):
        self.v2 = OntoLangParserV2()
        self.errors = []
        self.warnings = []

    def parse(self, source):
        ast = self.v2.parse(source)
        legacy = to_legacy_ast(ast)
        legacy["errors"] = [{"line": e.pos.line, "msg": e.msg} for e in self.v2.parser.errors]
        return legacy

    def validate(self, ast):
        if isinstance(ast, dict):
            return self._validate_dict(ast)
        return self.v2.validate(ast)

    def _validate_dict(self, ast):
        errors = []
        for e in ast.get("entities", []):
            prefix = e["id"].split("-")[0] if "-" in e["id"] else ""
            if prefix not in ("ORG", "ROL", "PRJ"):
                errors.append(f"E{e.get('line', 0)}: '{e['id']}' 前缀无效")
        for inf in ast.get("inferences", []):
            # 兼容 raw 字段和初始 dict 格式
            check_text = inf.get("raw", "") or str(inf.get("derives_from", "")) or ""
            if "derives_from" not in check_text and not inf.get("derives_from"):
                errors.append(f"E{inf.get('line', 0)}: '{inf['id']}' 缺少derives_from声明")
        for f in ast.get("facts", []):
            if not re.match(r'^(D-F|P-F)\d+', f["id"]):
                errors.append(f"E{f.get('line', 0)}: '{f['id']}' 事实ID格式无效")
        return errors

    def test_suite(self):
        legacy_ast, errors, parse_errors = self.v2.test_suite()
        self.errors = ["parse_error"] * parse_errors
        return legacy_ast
