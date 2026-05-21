"""Unit tests for OntoDerive Eidos adapter."""

import sys
from pathlib import Path
from importlib import import_module
from types import SimpleNamespace

WORKSPACE = Path(__file__).resolve().parents[2]
# Add both onto and eidos to path
sys.path.insert(0, str(WORKSPACE / "eidos" / "src"))
sys.path.insert(0, str(WORKSPACE / "engine"))


def test_to_eidos_entity_roundtrip():
    """OntoDerive Entity -> Eidos OntologyNode"""
    from engine.ecosystem.eidos_adapter import to_eidos_entity

    entity = SimpleNamespace(
        id="e1",
        node_type="concept",
        tags=["test"],
        data={"name": "Gravity"},
    )
    node = to_eidos_entity(entity)

    if node is None:
        import pytest

        pytest.skip("Eidos not available")

    assert node.id == "e1"
    assert node.name == "Gravity"
    assert node.node_type == "concept"
    assert "test" in node.aliases


def test_to_eidos_entity_empty_data():
    """Entity with empty data produces valid OntologyNode"""
    from engine.ecosystem.eidos_adapter import to_eidos_entity

    entity = SimpleNamespace(id="e2", node_type="empty", tags=[], data={})
    node = to_eidos_entity(entity)

    if node is None:
        import pytest

        pytest.skip("Eidos not available")

    assert node.id == "e2"
    assert node.name == "e2"  # falls back to id
    assert node.validate() == []


def test_from_eidos_entity():
    """Eidos OntologyNode -> OntoDerive Entity"""
    from engine.ecosystem.eidos_adapter import from_eidos_entity

    class MockNode:
        id = "m1"
        name = "Mock"
        node_type = "concept"
        properties = {"key": "val"}
        aliases = ["mock"]
        description = "test"

    entity = from_eidos_entity(MockNode())
    assert entity is not None
    assert entity.eid == "m1"
    assert entity.name == "Mock"
    assert entity.entity_type == "concept"


def test_from_eidos_entity_none():
    """None input returns None"""
    from engine.ecosystem.eidos_adapter import from_eidos_entity

    assert from_eidos_entity(None) is None


def test_from_eidos_entity_missing_fields():
    """Object with missing fields still works"""
    from engine.ecosystem.eidos_adapter import from_eidos_entity

    partial = SimpleNamespace(id="p1")
    # name, node_type, etc. are missing

    entity = from_eidos_entity(partial)
    assert entity is not None
    assert entity.eid == "p1"


def test_eidos_fact_roundtrip():
    """Eidos Fact -> OntoDerive FormalFact"""
    from engine.ecosystem.eidos_adapter import from_eidos_fact, to_eidos_fact

    try:
        Fact = import_module("eidos.types").Fact
    except ImportError:
        import pytest

        pytest.skip("Eidos not available")

    eidos_fact = Fact(id="f1", subject="Earth", predicate="orbits", object="Sun")
    onto_fact = from_eidos_fact(eidos_fact)

    assert onto_fact is not None
    assert onto_fact.fid == "f1"
    assert onto_fact.value == "Sun"
    assert onto_fact.confidence == 1.0

    # Roundtrip back
    back = to_eidos_fact(onto_fact)
    assert back is not None
    assert back.id == "f1"


def test_is_eidos_available():
    """is_eidos_available returns bool"""
    from engine.ecosystem.eidos_adapter import is_eidos_available

    assert isinstance(is_eidos_available(), bool)
