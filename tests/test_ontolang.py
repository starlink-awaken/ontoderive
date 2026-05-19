"""
测试OntoLang解析器
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from ontolang import OntoLangParser


def test_test_suite():
    parser = OntoLangParser()
    ast = parser.test_suite()
    assert len(ast["entities"]) == 2
    assert len(ast["facts"]) == 2
    assert len(ast["inferences"]) == 1
    assert len(ast["protocols"]) == 1


def test_validate_good_ast():
    parser = OntoLangParser()
    ast = parser.test_suite()
    errors = parser.validate(ast)
    assert errors == []


def test_validate_bad_entity():
    parser = OntoLangParser()
    ast = {
        "entities": [{"id": "BAD-xxx", "type": "BadType", "line": 1, "raw": "entity BAD-xxx : BadType {}"}],
        "facts": [], "inferences": [], "protocols": [],
    }
    errors = parser.validate(ast)
    assert len(errors) >= 1
    assert "前缀无效" in errors[0]


def test_validate_bad_fact():
    parser = OntoLangParser()
    ast = {
        "entities": [],
        "facts": [{"id": "BAD-F1", "type": "Bad", "line": 1, "raw": "fact BAD-F1 : Bad {}"}],
        "inferences": [], "protocols": [],
    }
    errors = parser.validate(ast)
    assert len(errors) >= 1


def test_validate_missing_derives_from():
    parser = OntoLangParser()
    ast = {
        "entities": [],
        "facts": [],
        "inferences": [{"id": "INF-L1", "type": "Test", "line": 1, "raw": "inference INF-L1 : Test {}"}],
        "protocols": [],
    }
    errors = parser.validate(ast)
    assert len(errors) >= 1
    assert "derives_from" in errors[0]


def test_parse_empty():
    parser = OntoLangParser()
    ast = parser.parse("")
    assert ast["entities"] == []
    assert ast["facts"] == []


def test_parse_comment():
    parser = OntoLangParser()
    ast = parser.parse("-- 这是注释\nentity ORG-TEST : Test {}")
    assert len(ast["entities"]) == 1
    assert ast["entities"][0]["id"] == "ORG-TEST"


def test_parse_multiple():
    parser = OntoLangParser()
    source = """entity ORG-A : Org {}
fact D-F1 : DataPoint {}
inference INF-L1 : Inf { derives_from: [D-F1] }
protocol P-001 : Constraint {}"""
    ast = parser.parse(source)
    assert len(ast["entities"]) == 1
    assert len(ast["facts"]) == 1
    assert len(ast["inferences"]) == 1
    assert len(ast["protocols"]) == 1
