"""
UnifiedReasoner — 统一推理引擎 (P1)
=====================================
合并 RuleReasoner + FormalReasoner 输出为统一格式。
确定性/启发式/结构性三层分类 + certainty标注。
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

from .reasoner import RuleReasoner
from .reasoner_formal import FormalReasoner, FormalConclusion


@dataclass
class UnifiedConclusion:
    conclusion: str
    certainty: str  # certain/probable/uncertain/structural
    method: str
    derives_from: List[str] = field(default_factory=list)
    confidence: float = 0.80
    source: str = ""  # rule_engine / formal / llm

    def to_dict(self):
        return asdict(self)


class UnifiedReasoner:
    """统一推理入口 — 合并RuleReasoner + FormalReasoner"""

    def __init__(self):
        self.rule = RuleReasoner()
        self.formal = FormalReasoner()

    def reason(self, facts: Dict, inferences: Dict, knowledge=None) -> List[UnifiedConclusion]:
        results = []

        # 1. 确定性推理 (RuleReasoner中的数学/逻辑必然结论)
        rr = self.rule.derive(facts, inferences)
        for r in rr:
            if r["type"] in ("numeric_comparison", "modus_ponens_valid", "subsumption",
                              "missing_reference", "chain_break", "threshold_alert"):
                results.append(UnifiedConclusion(
                    conclusion=r["conclusion"], certainty="certain",
                    method=r["type"], confidence=r.get("confidence", 0.90),
                    derives_from=r.get("derived_from", []), source="rule_engine",
                ))

        # 2. 启发式推理 (probable)
        for r in rr:
            if r["type"] in ("shared_premise", "disjunctive_syllogism", "evidence_gap",
                              "influence_analysis", "structural_hole", "transitive_dependency"):
                results.append(UnifiedConclusion(
                    conclusion=r["conclusion"], certainty="probable",
                    method=r["type"], confidence=r.get("confidence", 0.70),
                    derives_from=r.get("derived_from", []), source="rule_engine",
                ))

        # 3. 结构性分析
        for r in rr:
            if r["type"] in ("coverage", "redundancy_warning", "consistency_warning",
                              "temporal_sequence", "incremental_recalc", "case_match"):
                results.append(UnifiedConclusion(
                    conclusion=r["conclusion"], certainty="structural",
                    method=r["type"], confidence=r.get("confidence", 0.80),
                    derives_from=r.get("derived_from", []), source="rule_engine",
                ))

        # 4. 形式推理 (formal reasoner, 如果knowledge可用)
        if knowledge:
            for c in self.formal.reason(knowledge):
                results.append(UnifiedConclusion(
                    conclusion=c.conclusion, certainty=c.certainty,
                    method=c.method, confidence=c.confidence,
                    derives_from=c.derives_from, source="formal",
                ))

        return results

    def summary(self) -> Dict:
        return {
            "total": len(getattr(self, '_last_results', [])),
        }
