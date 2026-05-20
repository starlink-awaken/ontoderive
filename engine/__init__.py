"""OntoDerive — 渊衍框架 v3.5

知识工程分析平台。三模式：结构分析 | 规则推理 | 形式推理。
物理五层架构 + ToolForge工具匹配 + 分析模式引擎 + 连续推理谱系。

用法:
    from engine import OntoDerive, ToolForge, FormalPipeline
    od = OntoDerive("my-project").derive()
"""
__version__ = "3.5.0"

# 顶层 re-export — 保持向后兼容
from engine.core.derive import OntoDerive as _OntoDerive, VERSION as _VERSION
from engine.toolforge import ToolForge as _ToolForge
from engine.formalize import Formalizer as _Formalizer, FormalKnowledge as _FormalKnowledge
from engine.pipeline_v4 import FormalPipeline as _FormalPipeline

OntoDerive = _OntoDerive
VERSION = _VERSION
ToolForge = _ToolForge
Formalizer = _Formalizer
FormalKnowledge = _FormalKnowledge
FormalPipeline = _FormalPipeline

# 子包门面 — 可直接 from engine import xxx_layer
from engine import core, reasoners, theories, intelligence, foundation  # noqa: F401
