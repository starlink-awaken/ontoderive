"""OntoLang AST节点定义"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class NodeType(Enum):
    ENTITY = "entity"
    FACT = "fact"
    INFERENCE = "inference"
    PROTOCOL = "protocol"
    RELATION = "relation"


@dataclass
class SourcePos:
    line: int
    col: int
    file: str = ""

    def __str__(self):
        return f"{self.file}:{self.line}:{self.col}" if self.file else f"L{self.line}:C{self.col}"


@dataclass
class EntityDef:
    id: str
    entity_type: str
    properties: dict = field(default_factory=dict)
    pos: Optional[SourcePos] = None


@dataclass
class FactDef:
    id: str
    fact_type: str
    properties: dict = field(default_factory=dict)
    pos: Optional[SourcePos] = None


@dataclass
class InferenceDef:
    id: str
    inference_type: str
    derives_from: List[str] = field(default_factory=list)
    conclusion: str = ""
    properties: dict = field(default_factory=dict)
    pos: Optional[SourcePos] = None


@dataclass
class ProtocolDef:
    id: str
    constraint_type: str
    constraint: str = ""
    properties: dict = field(default_factory=dict)
    pos: Optional[SourcePos] = None


@dataclass
class RelationDef:
    subject: str
    relation_type: str
    object: str
    pos: Optional[SourcePos] = None


@dataclass
class AST:
    entities: List[EntityDef] = field(default_factory=list)
    facts: List[FactDef] = field(default_factory=list)
    inferences: List[InferenceDef] = field(default_factory=list)
    protocols: List[ProtocolDef] = field(default_factory=list)
    relations: List[RelationDef] = field(default_factory=list)


@dataclass
class ParseError:
    msg: str
    pos: SourcePos
    hint: str = ""


@dataclass
class SemanticError:
    msg: str
    node_id: str = ""
    pos: Optional[SourcePos] = None
    hint: str = ""
