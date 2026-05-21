"""Eidos adapter for OntoDerive — bidirectional bridge between formal models and Eidos schema types.
All functions gracefully degrade if Eidos is not available."""

from __future__ import annotations

EIDOS_AVAILABLE = False

try:
    from eidos.types import Fact as EidosFact  # type: ignore[reportMissingImports]
    from eidos.types import OntologyNode  # type: ignore[reportMissingImports]

    EIDOS_AVAILABLE = True
except ImportError:
    EidosFact = None  # type: ignore[assignment]
    OntologyNode = None  # type: ignore[assignment]


def is_eidos_available() -> bool:
    return EIDOS_AVAILABLE


def to_eidos_fact(onto_fact):
    if not EIDOS_AVAILABLE:
        return None
    assert EidosFact is not None
    data = getattr(onto_fact, "data", None) or {}
    fact_id = getattr(onto_fact, "id", getattr(onto_fact, "fid", ""))
    confidence = getattr(onto_fact, "weight", getattr(onto_fact, "confidence", 1.0))
    return EidosFact(
        id=fact_id,
        subject=data.get("subject", ""),
        predicate=data.get("predicate", "is"),
        object=data.get("object", ""),
        confidence=confidence,
        source_card_id=fact_id,
        derived_from="ontoderive",
    )


def from_eidos_fact(eidos_fact):
    from engine.foundation.models import Fact as FormalFact

    return FormalFact(
        fid=eidos_fact.id,
        description=f"{eidos_fact.subject} {eidos_fact.predicate} {eidos_fact.object}",
        value=eidos_fact.object,
        source=eidos_fact.source_card_id or eidos_fact.derived_from,
        confidence=eidos_fact.confidence,
        type="data",
    )


def to_eidos_entity(onto_entity):
    if not EIDOS_AVAILABLE:
        return None
    assert OntologyNode is not None
    data = getattr(onto_entity, "data", None) or {}
    aliases = list(getattr(onto_entity, "tags", []) or [])
    entity_id = getattr(onto_entity, "id", getattr(onto_entity, "eid", ""))
    node_type = getattr(onto_entity, "node_type", getattr(onto_entity, "entity_type", ""))
    return OntologyNode(
        id=entity_id,
        name=data.get("name", getattr(onto_entity, "name", entity_id)),
        node_type=node_type,
        properties={k: v for k, v in data.items() if k not in ("name",)},
        description=data.get("description", getattr(onto_entity, "role", "")),
        aliases=aliases,
    )


def from_eidos_entity(node):
    from engine.foundation.models import Entity as FormalEntity

    if node is None:
        return None

    properties = dict(getattr(node, "properties", {}) or {})
    return FormalEntity(
        eid=getattr(node, "id", ""),
        name=getattr(node, "name", ""),
        entity_type=getattr(node, "node_type", ""),
        role=getattr(node, "description", ""),
        count=str(properties.get("count", "")),
        facts_ref=list(getattr(node, "aliases", []) or []),
    )
