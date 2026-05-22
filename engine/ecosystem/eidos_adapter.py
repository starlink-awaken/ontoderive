"""Bidirectional bridge between OntoDerive models and Eidos types."""
EIDOS_AVAILABLE = False
try:
    from eidos.types import Fact, OntologyNode
    EIDOS_AVAILABLE = True
except ImportError:
    pass

def is_eidos_available():
    return EIDOS_AVAILABLE

def to_eidos_fact(onto_fact):
    if not EIDOS_AVAILABLE: return None
    d = getattr(onto_fact, 'data', {}) or {}
    return Fact(id=getattr(onto_fact, 'id', 'f'),
                subject=d.get('subject', ''), predicate=d.get('predicate', 'is'),
                object=d.get('object', ''), confidence=getattr(onto_fact, 'weight', 1.0),
                source_card_id=getattr(onto_fact, 'id', ''), derived_from='ontoderive')

def from_eidos_fact(ef):
    return type('FormalFact', (), {'id': ef.id, 'weight': ef.confidence, 'data': {'subject': ef.subject, 'predicate': ef.predicate, 'object': ef.object}})()

def to_eidos_entity(onto_entity):
    if not EIDOS_AVAILABLE: return None
    d = getattr(onto_entity, 'data', {}) or {}
    return OntologyNode(id=getattr(onto_entity, 'id', ''),
                        name=d.get('name', ''), node_type=getattr(onto_entity, 'node_type', 'entity'),
                        properties={k:v for k,v in d.items() if k != 'name'})
