"""
OntoDerive 规则推导引擎 — 无LLM的有限推导
=============================================
基于三段论模式+状态机的确定性推导。
不解析自然语言，不替代LLM。但对结构化数据有效。

能力边界:
✅ 数值比较推导 (D-F1 > D-F2 → 推论A)
✅ 阈值触发推导 (D-F1 < 基准 → 告警)
✅ 共享前提推导 (INF-A和INF-B引用同一组事实 → 可能互补/矛盾)
✅ 缺失证据检测 (推论引用了不存在的ID)
✅ 推导链完整性 (INF-L2引用INF-L1但INF-L1未定义)
❌ 自然语言语义理解
❌ 新概念的创造性发现
❌ 隐喻/类比推理
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path


@dataclass
class DerivationRule:
    """一条推导规则 = 三段论模式"""
    name: str
    premises: List[str]  # 前提模式(正则)
    conclusion_template: str  # 结论模板
    confidence: float = 0.85
    category: str = "deduction"  # deduction | induction | abduction


class RuleReasoner:
    """基于规则的确定性推导引擎 — 零依赖，永远可用"""

    def __init__(self):
        self.rules: List[DerivationRule] = self._default_rules()
        self.state = "idle"  # idle → collecting → deriving → done

    def _default_rules(self):
        """内置推导规则库 — 可扩展"""
        return [
            # ── 数值比较规则 ──
            DerivationRule(
                name="numeric_comparison",
                premises=["D-F\\d+.*?(\\d+\\.?\\d*).*?(\\d+\\.?\\d*)"],
                conclusion_template="数值比较: {label1}={val1} vs {label2}={val2}",
                confidence=0.95,
                category="deduction",
            ),
            # ── 共享前提规则 ──
            DerivationRule(
                name="shared_premise_alert",
                premises=[],
                conclusion_template="INF-{a}和INF-{b}共享{n}个前提事实，可能互补或矛盾",
                confidence=0.75,
                category="induction",
            ),
            # ── 缺失引用规则 ──
            DerivationRule(
                name="missing_reference",
                premises=[],
                conclusion_template="推论 {inf} 引用了不存在的事实 {fid}",
                confidence=0.99,
                category="deduction",
            ),
            # ── 证据缺口规则 ──
            DerivationRule(
                name="evidence_gap",
                premises=[],
                conclusion_template="推论 {inf} 基于{n}个前提，建议增加引用以增强可信度",
                confidence=0.80,
                category="induction",
            ),
            # ── 阈值触发规则 ──
            DerivationRule(
                name="threshold_alert",
                premises=[],
                conclusion_template="{metric}达到{value}，超过基准{threshold}",
                confidence=0.90,
                category="deduction",
            ),
        ]

    def derive(self, facts: Dict[str, dict], inferences: Dict[str, dict]) -> List[dict]:
        """
        基于规则库做确定性推导。
        facts: {id: {desc, value, ...}}   inferences: {title: {text, derives_from, ...}}
        """
        self.state = "deriving"
        results = []

        # R1: 数值比较 — 从事实中提取可比较的数值
        results.extend(self._numeric_derive(facts))

        # R2: 共享前提检测 — 找互相引用同一事实的推论
        results.extend(self._shared_premise_check(inferences))

        # R3: 缺失引用检测 — 推论引用了不存在的ID
        all_ids = set(facts.keys()) | set(inferences.keys())
        results.extend(self._missing_ref_check(inferences, all_ids))

        # R4: 证据缺口 — 引用太少的前提
        results.extend(self._evidence_gap_check(inferences))

        # R5: 阈值触发 — 从事实值对比预设阈值
        results.extend(self._threshold_check(facts))

        # R6: 推导链完整性 — INF引用INF但存在断链
        results.extend(self._chain_integrity_check(inferences))

        # R7: 假言推理 — 蕴含链检测 (Modus Ponens/Tollens)
        results.extend(self._modus_ponens_check(inferences, facts))

        # R8: 传递推理 — 属性传递链 (A→B→C ∴ A→C)
        results.extend(self._transitive_closure(inferences, facts))

        # R9: 包含推理 — 本体层级 (Subsumption: ORG ⊑ Entity)
        results.extend(self._subsumption_check(inferences, facts))

        # R10: 影响传播 — 图中心性 (哪个事实影响最大)
        results.extend(self._influence_analysis(inferences, facts))

        # R11: 冗余检测 — 结构推理
        results.extend(self._redundancy_check(inferences))

        # R12: 覆盖度分析
        results.extend(self._coverage_analysis(inferences, facts))

        self.state = "done"
        return results

    # ═══ R7: 假言推理 (Modus Ponens/Tollens) ═══

    def _modus_ponens_check(self, inferences, facts):
        """如果A成立且A→B, 则B成立。检测蕴含链的假设满足度"""
        results = []
        for title, info in inferences.items():
            premises = info.get("derives_from", [])
            satisfied = [p for p in premises if p in facts or p in inferences]
            if len(satisfied) < len(premises):
                missing = [p for p in premises if p not in satisfied]
                results.append({
                    "type": "modus_ponens_fail",
                    "conclusion": f"推论'{title[:30]}'的前提{missing}不成立, 推论有效性存疑",
                    "derived_from": premises,
                    "confidence": 0.85,
                    "method": "rule_engine",
                })
            elif len(satisfied) >= len(premises) >= 2:
                results.append({
                    "type": "modus_ponens_valid",
                    "conclusion": f"推论'{title[:30]}'的{len(premises)}个前提全部成立, 推论有效",
                    "derived_from": premises,
                    "confidence": 0.90,
                    "method": "rule_engine",
                })
        return results

    # ═══ R8: 传递推理 (Transitive Closure) ═══

    def _transitive_closure(self, inferences, facts):
        """A→B→C, 则A间接影响C。计算传递闭包"""
        results = []
        for title, info in inferences.items():
            indirect_deps = set()
            direct = set(info.get("derives_from", []))
            queue = list(direct)
            while queue:
                dep = queue.pop(0)
                if dep in inferences:
                    for grandparent in inferences[dep].get("derives_from", []):
                        if grandparent not in direct and grandparent not in indirect_deps:
                            indirect_deps.add(grandparent)
                            queue.append(grandparent)
            if indirect_deps:
                results.append({
                    "type": "transitive_dependency",
                    "conclusion": f"推论'{title[:30]}'间接依赖{len(indirect_deps)}个前提: {list(indirect_deps)[:5]}",
                    "derived_from": list(indirect_deps),
                    "confidence": 0.75,
                    "method": "rule_engine",
                })
        return results

    # ═══ R9: 包含推理 (Ontology Subsumption) ═══

    ONTOLOGY_HIERARCHY = {
        "DOMAIN": ["ORG", "ROL", "PRJ", "RES"],
        "FACT": ["DAT", "POL"],
        "INFERENCE": ["CONTRADICTION", "BUSINESS", "ARCHITECTURE"],
        "STATE": ["T", "F", "H"],
        "DOCUMENT": ["COL", "DOC", "CH", "SEC"],
    }

    def _subsumption_check(self, inferences, facts):
        """A ⊑ B (A是B的子类), x ∈ A ∴ x ∈ B
        检测实体ID是否使用了正确的上层类型"""
        results = []
        all_ids = list(inferences.keys()) + list(facts.keys())
        type_map = {}
        for id_str in all_ids:
            prefix = id_str.split("-")[0] if "-" in id_str else id_str[:3]
            type_map[id_str] = prefix

        # 检查: ORG-xxx被正确归类为DOMAIN的子类型
        for parent_type, subtypes in self.ONTOLOGY_HIERARCHY.items():
            for id_str, prefix in type_map.items():
                if prefix in subtypes:
                    # 正确归类, 通过
                    pass
                elif prefix in sum([v for k, v in self.ONTOLOGY_HIERARCHY.items() if k != parent_type], []):
                    # 前缀属于另一个父类型 → 可能归类错误
                    pass
        # 简化输出
        n_correct = sum(1 for p in type_map.values() for v in self.ONTOLOGY_HIERARCHY.values() if p in v)
        n_total = len(type_map)
        if n_total > 0 and n_correct < n_total:
            results.append({
                "type": "subsumption",
                "conclusion": f"{n_correct}/{n_total}个ID正确归入本体层级({','.join(self.ONTOLOGY_HIERARCHY.keys())})",
                "derived_from": [],
                "confidence": 0.70,
                "method": "rule_engine",
            })
        return results

    # ═══ R10: 影响传播 (Influence Analysis) ═══

    def _influence_analysis(self, inferences, facts):
        """计算每个事实/推论的'影响力' = 被多少推论直接/间接引用"""
        results = []
        influence = {}
        for title, info in inferences.items():
            for dep in info.get("derives_from", []):
                influence[dep] = influence.get(dep, 0) + 1
        if influence:
            top = sorted(influence.items(), key=lambda x: -x[1])[:3]
            top_str = "; ".join(f"{k}(被{count}个推论引用)" for k, count in top)
            results.append({
                "type": "influence_analysis",
                "conclusion": f"最具影响力的前提: {top_str}",
                "derived_from": [k for k, _ in top],
                "confidence": 0.80,
                "method": "rule_engine",
            })
        return results

    # ═══ R11: 冗余检测 (Redundancy Check) ═══

    def _redundancy_check(self, inferences):
        """检测推论间的冗余 — 共享3+前提且文本相似"""
        results = []
        inf_list = list(inferences.items())
        for i in range(len(inf_list)):
            for j in range(i + 1, len(inf_list)):
                a_id, a_info = inf_list[i]
                b_id, b_info = inf_list[j]
                shared = set(a_info.get("derives_from", [])) & set(b_info.get("derives_from", []))
                if len(shared) >= 3:
                    results.append({
                        "type": "redundancy_warning",
                        "conclusion": f"'{a_id[:25]}'和'{b_id[:25]}'共享{len(shared)}个前提, 可能冗余",
                        "derived_from": list(shared),
                        "confidence": 0.65,
                        "method": "rule_engine",
                    })
        return results

    # ═══ R12: 覆盖度分析 (Coverage Analysis) ═══

    def _coverage_analysis(self, inferences, facts):
        """分析事实被推论引用的覆盖率"""
        results = []
        if not facts:
            return results
        cited = set()
        for info in inferences.values():
            cited.update(info.get("derives_from", []))
        fact_ids = set(facts.keys())
        cited_facts = fact_ids & cited
        uncited = fact_ids - cited
        rate = len(cited_facts) / len(fact_ids) * 100 if fact_ids else 100
        results.append({
            "type": "coverage",
            "conclusion": f"事实覆盖率{rate:.0f}%({len(cited_facts)}/{len(fact_ids)}), 未引用: {list(uncited)[:5]}",
            "derived_from": list(uncited),
            "confidence": 0.95,
            "method": "rule_engine",
        })
        return results

    def _numeric_derive(self, facts):
        """R1: 数值比较推导 — 三段论最直接的体现"""
        results = []
        numeric = {}
        for fid, info in facts.items():
            m = re.search(r'(\d+\.?\d*)', str(info.get("value", "")))
            if m:
                numeric[fid] = {"label": info.get("desc", fid)[:30], "value": float(m.group(1))}

        # 两两比较
        ids = list(numeric.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = numeric[ids[i]], numeric[ids[j]]
                if b["value"] > 0 and a["value"] > b["value"] * 1.5:  # 显著差异
                    results.append({
                        "type": "numeric_comparison",
                        "conclusion": f"{a['label']}({a['value']})是{b['label']}({b['value']})的{a['value']/b['value']:.1f}倍",
                        "derived_from": [ids[i], ids[j]],
                        "confidence": 0.95,
                        "method": "rule_engine",
                    })
        return results

    def _shared_premise_check(self, inferences):
        """R2: 共享前提检测 — 两个推论引用相同事实可能互补或矛盾"""
        results = []
        inf_list = list(inferences.items())
        for i in range(len(inf_list)):
            for j in range(i + 1, len(inf_list)):
                a_id, a_info = inf_list[i]
                b_id, b_info = inf_list[j]
                shared = set(a_info.get("derives_from", [])) & set(b_info.get("derives_from", []))
                if len(shared) >= 2:
                    results.append({
                        "type": "shared_premise",
                        "conclusion": f"推论'{a_id[:30]}'和'{b_id[:30]}'共享{len(shared)}个前提({list(shared)[:3]})",
                        "derived_from": list(shared),
                        "confidence": 0.75,
                        "method": "rule_engine",
                    })
        return results

    def _missing_ref_check(self, inferences, all_ids):
        """R3: 缺失引用 — 三段论的前提断裂"""
        results = []
        for title, info in inferences.items():
            for ref in info.get("derives_from", []):
                if ref not in all_ids:
                    results.append({
                        "type": "missing_reference",
                        "conclusion": f"推论'{title[:30]}'引用了未定义的'{ref}'",
                        "derived_from": [ref],
                        "confidence": 0.99,
                        "method": "rule_engine",
                    })
        return results

    def _evidence_gap_check(self, inferences):
        """R4: 证据缺口 — 前提不足以支持推论"""
        results = []
        for title, info in inferences.items():
            n = len(info.get("derives_from", []))
            if 0 < n < 2:
                results.append({
                    "type": "evidence_gap",
                    "conclusion": f"推论'{title[:30]}'仅{n}个前提，建议增加到2+",
                    "derived_from": info.get("derives_from", []),
                    "confidence": 0.80,
                    "method": "rule_engine",
                })
        return results

    def _threshold_check(self, facts, thresholds=None):
        """R5: 阈值触发 — 预设基准检查"""
        if thresholds is None:
            thresholds = {
                "转化率": 10.0, "成功率": 80.0, "覆盖率": 60.0,
                "满意度": 70.0, "测试覆盖率": 60.0,
            }
        results = []
        for fid, info in facts.items():
            desc = info.get("desc", "")
            for metric, threshold in thresholds.items():
                if metric in desc:
                    m = re.search(r'(\d+\.?\d*)', str(info.get("value", "")))
                    if m:
                        val = float(m.group(1))
                        if val < threshold:
                            results.append({
                                "type": "threshold_alert",
                                "conclusion": f"{desc}({val})低于基准{threshold}",
                                "derived_from": [fid],
                                "confidence": 0.90,
                                "method": "rule_engine",
                            })
        return results

    def _chain_integrity_check(self, inferences):
        """R6: 推导链完整性 — INF→INF链是否完整"""
        results = []
        inf_ids = set(inferences.keys())
        for title, info in inferences.items():
            for ref in info.get("derives_from", []):
                if ref.startswith("INF") and ref not in inf_ids:
                    results.append({
                        "type": "chain_break",
                        "conclusion": f"推导链断裂: '{title[:30]}'引用了未定义的'{ref}'",
                        "derived_from": [ref],
                        "confidence": 0.99,
                        "method": "rule_engine",
                    })
        # 检测推导深度
        depths = {}
        for title in inferences:
            self._calc_depth(title, inferences, depths, set())
        max_depth = max(depths.values()) if depths else 0
        if max_depth <= 1 and len(inferences) >= 3:
            results.append({
                "type": "shallow_chain",
                "conclusion": f"推导链深度仅{max_depth}，{len(inferences)}个推论间缺少递进关系",
                "derived_from": [],
                "confidence": 0.70,
                "method": "rule_engine",
            })
        return results

    def _calc_depth(self, node, inferences, depths, visited):
        if node in visited or node not in inferences:
            depths[node] = 0
            return 0
        visited.add(node)
        max_parent = 0
        for parent in inferences[node].get("derives_from", []):
            if parent.startswith("INF"):
                max_parent = max(max_parent, self._calc_depth(parent, inferences, depths, visited))
        depths[node] = max_parent + 1
        return depths[node]
