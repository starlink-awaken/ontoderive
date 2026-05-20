"""
分析模式引擎 — Analytical Patterns Engine
============================================
将领域知识(博弈论/经济学/组织行为学/策略规划)编码为可复用的分析模板。
每个模式 = 检测规则(确定性) + 分析逻辑(公式/LLM增强) → 统一结论

与推理规则的区别:
  推理规则(R1-R19): 回答"推导对不对" — 逻辑一致性
  分析模式(A1-Ax):  回答"这意味着什么" — 领域洞察
"""
import re
from dataclasses import dataclass
from typing import List, Callable


@dataclass
class AnalyticalPattern:
    """分析模式定义"""
    name: str
    description: str
    category: str  # game_theory | economics | supply_chain | organizational | strategic
    detect: Callable  # (facts, entities, relations) → bool
    analyze: Callable  # (facts, entities, relations, enhancer) → List[dict]
    requires_llm: bool = False


class AnalyticsEngine:
    """分析模式引擎 — 确定性检测 + 可选的LLM增强"""

    def __init__(self, enhancer=None):
        self.enhancer = enhancer
        self.patterns = self._register_patterns()

    def _register_patterns(self):
        return [
            # ═══ A1: 供给弹性分析 ═══
            AnalyticalPattern(
                name="capacity_elasticity",
                description="检测产能/库存约束, 估算供给弹性",
                category="economics",
                detect=self._detect_capacity_constraint,
                analyze=self._analyze_capacity,
                requires_llm=False,
            ),
            # ═══ A2: 供应链风险放大 ═══
            AnalyticalPattern(
                name="supply_chain_amplification",
                description="沿depends_on链计算风险传导放大系数",
                category="supply_chain",
                detect=self._detect_supply_risk,
                analyze=self._analyze_supply_chain,
                requires_llm=False,
            ),
            # ═══ A3: 代理问题检测 ═══
            AnalyticalPattern(
                name="principal_agent",
                description="检测employs关系中法律雇主≠实际服务对象的代理问题",
                category="game_theory",
                detect=self._detect_agency_issue,
                analyze=self._analyze_agency,
                requires_llm=True,  # 需要LLM理解组织上下文
            ),
            # ═══ A4: 激励不相容检测 ═══
            AnalyticalPattern(
                name="incentive_misalignment",
                description="对比各实体的目标与激励结构, 检测错位",
                category="organizational",
                detect=self._detect_incentive_issue,
                analyze=self._analyze_incentive,
                requires_llm=True,
            ),
            # ═══ A5: 分阶段补救规划 ═══
            AnalyticalPattern(
                name="remediation_planning",
                description="基于问题严重度和可行性生成短/中/长期行动方案",
                category="strategic",
                detect=self._detect_remediation_needed,
                analyze=self._analyze_remediation,
                requires_llm=True,
            ),
        ]

    def run(self, facts, entities, inferences, relations=None, patterns=None):
        """运行所有(或指定)分析模式, 返回洞察列表"""
        # 防御: 确保facts是dict
        if not isinstance(facts, dict):
            return []
        results = []
        targets = patterns or self.patterns
        for pat in targets:
            try:
                if pat.detect(facts, entities, relations or []):
                    conclusions = pat.analyze(facts, entities, relations or [], self.enhancer)
                    for c in conclusions:
                        c["pattern"] = pat.name
                        c["category"] = pat.category
                    results.extend(conclusions)
            except Exception as e:
                # 静默降级: 分析模式失败不影响主流程
                pass
        return results

    # ═══ A1: 供给弹性 ═══

    def _detect_capacity_constraint(self, facts, entities, relations):
        """检测: 产能利用率>90% 或 库存<安全基准"""
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            val = info.get("value", "")
            if ("利用率" in desc or "产能" in desc) and _extract_num(val) > 90:
                return True
            if "库存" in desc:
                stock = _extract_num(val)
                # 查找对应安全基准
                for fid2, info2 in _iter_facts(facts):
                    if "安全" in info2.get("desc", "") and _extract_num(info2.get("value", "")) > stock:
                        return True
        return False

    def _analyze_capacity(self, facts, entities, relations, enhancer):
        results = []
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            val = info.get("value", "")
            num = _extract_num(val)
            if num <= 0:
                continue
            # 利用率分析
            if "利用率" in desc and num > 90:
                elasticity = max(0, (100 - num) / num)  # 剩余产能比例
                results.append({
                    "type": "analytics",
                    "conclusion": f"供给弹性≈{elasticity:.2f}: '{desc}'={val}, "
                                  f"仅余{100-num:.0f}%产能, 需求波动将直接传导为短缺",
                    "derives_from": [fid],
                    "confidence": 0.85,
                })
            # 库存vs安全基准
            if "库存" in desc:
                for fid2, info2 in _iter_facts(facts):
                    if "安全" in info2.get("desc", ""):
                        safe = _extract_num(info2.get("value", ""))
                        if safe > num:
                            gap_pct = (safe - num) / safe * 100
                            results.append({
                                "type": "analytics",
                                "conclusion": f"库存缺口: '{desc}'={val}低于安全基准{safe}, "
                                              f"缺口{gap_pct:.0f}%, 补库压力紧迫",
                                "derives_from": [fid, fid2],
                                "confidence": 0.90,
                            })
        return results

    # ═══ A2: 供应链风险放大 ═══

    def _detect_supply_risk(self, facts, entities, relations):
        """检测: 存在depends_on链 + 交付/库存异常"""
        has_chain = any(r.get("relation_type") == "depends_on" for r in (relations or []))
        has_issue = any(
            "交付" in (f.get("desc", "") + f.get("description", ""))
            and _extract_num(f.get("value", "")) < 80
            for _, f in _iter_facts(facts)
        )
        return has_chain and has_issue

    def _analyze_supply_chain(self, facts, entities, relations, enhancer):
        results = []
        # 构建依赖图
        deps = {}  # {downstream: [(upstream, dependency_ratio), ...]}
        for r in (relations or []):
            if r.get("relation_type") == "depends_on":
                deps.setdefault(r["subject"], []).append((r["object"], 1.0))

        # 查找交付异常
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            if "交付" not in desc:
                continue
            delivery = _extract_num(info.get("value", ""))
            if delivery >= 80 or delivery <= 0:
                continue
            # 查找该实体的上游依赖
            entity_name = _find_entity_for_fact(fid, desc, entities)
            upstreams = deps.get(entity_name, [])
            for up_name, ratio in upstreams:
                # 查找上游的库存/利用率数据
                for fid2, info2 in _iter_facts(facts):
                    up_desc = info2.get("desc", "")
                    if "库存" in up_desc:
                        stock = _extract_num(info2.get("value", ""))
                        amplification = (100 - delivery) / 100 * ratio
                        results.append({
                            "type": "analytics",
                            "conclusion": f"风险传导: {entity_name}交付{delivery}%→上游{up_name}"
                                          f"库存{stock}天, 放大系数≈{amplification:.2f}",
                            "derives_from": [fid, fid2],
                            "confidence": 0.75,
                        })
        return results

    # ═══ A3: 代理问题 ═══

    def _detect_agency_issue(self, facts, entities, relations):
        """检测: X employs Y, 且Y的工作输出实际服务于Z(≠X)"""
        employs_pairs = [(r["subject"], r["object"])
                         for r in (relations or [])
                         if r.get("relation_type") == "employs"]
        if not employs_pairs:
            return False
        # 检查被雇佣方是否通过其他关系服务于第三方
        for employer, employee in employs_pairs:
            for r in (relations or []):
                if r.get("subject") == employee and r.get("relation_type") in (
                    "cooperates_with", "depends_on", "influences"
                ) and r.get("object") != employer:
                    return True
        return False

    def _analyze_agency(self, facts, entities, relations, enhancer):
        results = []
        employs_pairs = [(r["subject"], r["object"])
                         for r in (relations or [])
                         if r.get("relation_type") == "employs"]
        for employer, employee in employs_pairs:
            for r in (relations or []):
                if r.get("subject") == employee and r.get("object") != employer:
                    base = (f"潜在代理问题: {employer} employs {employee}, "
                            f"但{employee}的'{r['relation_type']}'关系指向{r['object']}")
                    if enhancer and enhancer.available:
                        try:
                            enhanced = enhancer._call(
                                f"分析以下代理问题的组织影响(一句话): {base}",
                                "你是组织行为学专家。", 0.3
                            )
                            if enhanced:
                                base += f"。LLM分析: {enhanced.strip()[:200]}"
                        except Exception:
                            pass
                    results.append({
                        "type": "analytics",
                        "conclusion": base,
                        "derives_from": [employer, employee, r.get("object", "")],
                        "confidence": 0.70,
                    })
        return results

    # ═══ A4: 激励不相容 ═══

    def _detect_incentive_issue(self, facts, entities, relations):
        """检测: 多实体存在 + 共享资源 + 不同目标"""
        # 简化为: 3个以上实体 + 至少1个共享关系
        n_entities = len(entities) if isinstance(entities, dict) else len(entities)
        n_relations = len(relations) if relations else 0
        return n_entities >= 3 and n_relations >= 2

    def _analyze_incentive(self, facts, entities, relations, enhancer):
        results = []
        # 找共享同一资源的不同实体
        targets = {}  # {target: [subjects]}
        for r in (relations or []):
            obj = r.get("object", "")
            targets.setdefault(obj, []).append(r.get("subject", ""))

        shared = [(t, subs) for t, subs in targets.items() if len(subs) >= 2]
        for target, subjects in shared:
            if enhancer and enhancer.available:
                try:
                    context = f"实体{', '.join(subjects)}共享资源{target}"
                    analysis = enhancer._call(
                        f"分析潜在激励不相容(一句话): {context}",
                        "你是组织行为学专家。", 0.3
                    )
                    if analysis:
                        results.append({
                            "type": "analytics",
                            "conclusion": f"激励不相容: {context}。{analysis.strip()[:200]}",
                            "derives_from": subjects + [target],
                            "confidence": 0.65,
                        })
                except Exception:
                    pass
        return results

    # ═══ A5: 补救规划 ═══

    def _detect_remediation_needed(self, facts, entities, relations):
        """检测: 存在'问题'/'审计'/'整改'相关事实或推论"""
        for _, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            if any(kw in desc for kw in ("审计", "整改", "问题", "风险", "违规", "差距")):
                return True
        return False

    def _analyze_remediation(self, facts, entities, relations, enhancer):
        results = []
        problems = []
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            val = info.get("value", "")
            if any(kw in desc for kw in ("审计问题", "高风险", "整改率", "认证", "差距")):
                problems.append(f"{desc}={val}")
        if not problems:
            return results

        # 确定性部分: 严重度分类
        high_risk = sum(1 for p in problems if "高风险" in p or "差距" in p)
        if high_risk > 0:
            results.append({
                "type": "analytics",
                "conclusion": f"短期(0-3月)优先: 解决{high_risk}个高风险项, 防止监管执法触发",
                "derives_from": [fid for fid in facts],
                "confidence": 0.80,
            })

        if enhancer and enhancer.available:
            try:
                context = "; ".join(problems[:8])
                plan = enhancer._call(
                    f"基于以下问题生成分阶段补救方案(短/中/长期各1-2句话): {context}",
                    "你是战略规划专家。", 0.4
                )
                if plan:
                    results.append({
                        "type": "analytics",
                        "conclusion": f"分阶段方案: {plan.strip()[:300]}",
                        "derives_from": [fid for fid in facts if any(
                            kw in facts[fid].get("desc", "") for kw in ("审计", "整改", "问题"))],
                        "confidence": 0.65,
                    })
            except Exception:
                pass
        return results


def _is_dict(val):
    return isinstance(val, dict)

def _iter_facts(facts):
    """安全迭代facts — 过滤非dict值"""
    if not isinstance(facts, dict):
        return
    for fid, info in facts.items():
        if _is_dict(info):
            yield fid, info

def _extract_num(val):
    """从值中提取数字"""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, bool):
        return 0.0
    m = re.search(r'(\d+\.?\d*)', str(val))
    return float(m.group(1)) if m else 0.0

def _safe_get(items, key, default=None):
    """安全获取dict值 — 兼容dict和原始值"""
    if isinstance(items, dict):
        return items.get(key, default)
    return default


def _find_entity_for_fact(fid, desc, entities):
    """根据事实描述找到对应实体ID"""
    if isinstance(entities, dict):
        for eid, info in entities.items():
            if info.get("name", "") in desc:
                return eid
    return fid
