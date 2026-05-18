"""生态适配器统一入口"""
from .minerva import minerva_to_facts, minerva_to_entities
from .sophia import sophia_to_toolforge, recommend_frameworks, get_derivation_guide
from .agora import AgoraAdapter
from .ecos import ECOSObserver, create_observer
