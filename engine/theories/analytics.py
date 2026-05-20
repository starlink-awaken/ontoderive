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
from typing import Callable

from engine.foundation.semantic import SemanticMatcher


@dataclass
class AnalyticalPattern:
    """分析模式定义

    semantic_depth: 0-5连续推理深度
      0 = 纯正则/数值比较 (R1-R18级别)
      1 = 语义匹配 (TF-IDF)
      2 = 嵌入向量 (需外部模型)
      3 = 轻量分类器
      4 = 小语言模型 (本地)
      5 = 大语言模型 (云端LLM)
    """
    name: str
    description: str
    category: str  # game_theory | economics | supply_chain | organizational | strategic
    detect: Callable  # (facts, entities, relations) → bool
    analyze: Callable  # (facts, entities, relations, enhancer) → List[dict]
    semantic_depth: int = 0  # 0-5连续推理深度
    requires_llm: bool = False  # 向后兼容, 等同于 semantic_depth >= 4


class AnalyticsEngine:
    """分析模式引擎 — 确定性检测 + 可选的LLM增强"""

    def __init__(self, enhancer=None, matcher=None):
        self.enhancer = enhancer
        self.matcher = matcher  # 语义匹配器 (v3.4 fix)
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
                semantic_depth=0,  # 纯公式计算
            ),
            # ═══ A2: 供应链风险放大 ═══
            AnalyticalPattern(
                name="supply_chain_amplification",
                description="沿depends_on链计算风险传导放大系数",
                category="supply_chain",
                detect=self._detect_supply_risk,
                analyze=self._analyze_supply_chain,
                semantic_depth=1,  # TF-IDF语义匹配
            ),
            # ═══ A3: 代理问题检测 ═══
            AnalyticalPattern(
                name="principal_agent",
                description="检测employs关系中法律雇主≠实际服务对象的代理问题",
                category="game_theory",
                detect=self._detect_agency_issue,
                analyze=self._analyze_agency,
                semantic_depth=4,  # 需要LLM理解组织上下文
            ),
            # ═══ A4: 激励不相容检测 ═══
            AnalyticalPattern(
                name="incentive_misalignment",
                description="对比各实体的目标与激励结构, 检测错位",
                category="organizational",
                detect=self._detect_incentive_issue,
                analyze=self._analyze_incentive,
                semantic_depth=1,  # TF-IDF语义匹配 (v3.4升级)
            ),
            # ═══ A5: 分阶段补救规划 ═══
            AnalyticalPattern(
                name="remediation_planning",
                description="基于问题严重度和可行性生成短/中/长期行动方案",
                category="strategic",
                detect=self._detect_remediation_needed,
                analyze=self._analyze_remediation,
                semantic_depth=1,  # 确定性计算+可选LLM增强
            ),
            # ═══ A6: 市场结构分析 ═══
            AnalyticalPattern(
                name="market_structure",
                description="实体数量+份额分布→HHI集中度+市场类型判定",
                category="economics",
                detect=self._detect_market_structure,
                analyze=self._analyze_market_structure,
                semantic_depth=0,  # 纯公式计算
            ),
            # ═══ A7: 博弈均衡检测 ═══
            AnalyticalPattern(
                name="game_equilibrium",
                description="多方竞争/合作/博弈关系→均衡类型+囚徒困境识别",
                category="game_theory",
                detect=self._detect_game_equilibrium,
                analyze=self._analyze_game_equilibrium,
                semantic_depth=1,  # TF-IDF语义匹配
            ),
            # ═══ A8: 策略选项生成 ═══
            AnalyticalPattern(
                name="strategic_options",
                description="目标+约束+资源→可行策略+风险收益评分",
                category="strategic",
                detect=self._detect_strategic_options,
                analyze=self._analyze_strategic_options,
                semantic_depth=2,  # 嵌入向量级别
            ),
        ]

    def run(self, facts, entities, inferences, relations=None, patterns=None,
            max_depth: int = 5):
        """运行所有(或指定)分析模式, 返回洞察列表

        max_depth: 最大推理深度 (0=仅纯规则, 3=含分类器, 5=含LLM)
        """
        if not isinstance(facts, dict):
            return []
        # 可用深度: 有enhancer→max 5, 有matcher→max 1, 否则→0
        available_depth = 0
        if self.enhancer and self.enhancer.available:
            available_depth = 5
        elif hasattr(self, 'matcher') and self.matcher:
            available_depth = 1
        effective_depth = min(max_depth, available_depth)

        results = []
        targets = patterns or self.patterns
        for pat in targets:
            # 深度控制: 只运行深度在可用范围内的模式
            if pat.semantic_depth > effective_depth:
                continue
            try:
                if pat.detect(facts, entities, relations or []):
                    conclusions = pat.analyze(facts, entities, relations or [], self.enhancer)
                    for c in conclusions:
                        c["pattern"] = pat.name
                        c["category"] = pat.category
                        c["semantic_depth"] = pat.semantic_depth
                    results.extend(conclusions)
            except Exception:
                pass
        return results

    # ═══ A1: 供给弹性 ═══

    def _detect_capacity_constraint(self, facts, entities, relations):
        """检测: 利用率>90%供给紧张 或 利用率<60%产能过剩 或 库存偏离基准"""
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            val = info.get("value", "")
            if ("利用率" in desc or "产能" in desc):
                num = _extract_num(val)
                if num > 90 or (num > 0 and num < 60):
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
            # 利用率分析 (供给紧张)
            if "利用率" in desc and num > 90 and num <= 100:
                elasticity = max(0, (100 - num) / num)  # 剩余产能比例
                results.append({
                    "type": "analytics",
                    "conclusion": f"供给弹性≈{elasticity:.2f}: '{desc}'={val}, "
                                  f"仅余{100-num:.0f}%产能, 需求波动将直接传导为短缺",
                    "derives_from": [fid],
                    "confidence": 0.85,
                })
            # 产能过剩检测 (v3.4)
            elif "利用率" in desc and num > 0 and num < 60:
                excess_pct = 100 - num
                results.append({
                    "type": "analytics",
                    "conclusion": f"产能过剩: '{desc}'={val}, 闲置{excess_pct:.0f}%产能, "
                                  f"供过于求→价格下行→行业出清压力",
                    "derives_from": [fid],
                    "confidence": 0.80,
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
        # 语义匹配器: 基于事实描述
        descs = [info.get("desc", "") for _, info in _iter_facts(facts)]
        matcher = SemanticMatcher(descs if descs else ["default"])
        # 构建依赖图
        deps = {}
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
            entity_name = _find_entity_for_fact(fid, desc, entities, matcher)
            upstreams = deps.get(entity_name, [])
            if not upstreams:
                for subj in deps:
                    if matcher.is_semantically_related(subj, desc):
                        upstreams = deps.get(subj, [])
                        entity_name = subj
                        break
            for up_name, ratio in upstreams:
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
        """检测: 多实体共享资源(语义关联) + 有不同的事实描述"""
        # 找共享同一目标实体的多个主体
        targets = {}
        for r in (relations or []):
            obj = r.get("object", "")
            targets.setdefault(obj, []).append(r.get("subject", ""))
        shared_resources = [(t, subs) for t, subs in targets.items() if len(subs) >= 2]
        return len(shared_resources) >= 1

    def _analyze_incentive(self, facts, entities, relations, enhancer):
        results = []
        # 匹配器: 用事实描述语料
        fact_desc = [f.get("desc", "") for f in facts.values() if isinstance(f, dict)]
        matcher = SemanticMatcher(fact_desc if fact_desc else ["default"])

        targets = {}
        for r in (relations or []):
            obj = r.get("object", "")
            targets.setdefault(obj, []).append(r.get("subject", ""))

        shared = [(t, subs) for t, subs in targets.items() if len(subs) >= 2]
        for target, subjects in shared:
            # 检测: 共享同一资源的实体是否有语义差异大的事实
            subj_facts = {}
            for fid, info in _iter_facts(facts):
                desc = info.get("desc", "")
                for subj in subjects:
                    if matcher.is_semantically_related(desc, subj, threshold=0.15):
                        subj_facts.setdefault(subj, []).append(desc)
            if len(subj_facts) >= 2:
                pairs = list(subj_facts.items())
                for i in range(len(pairs)):
                    for j in range(i + 1, len(pairs)):
                        s1, f1 = pairs[i]
                        s2, f2 = pairs[j]
                        if matcher.is_semantically_related(" ".join(f1), " ".join(f2), threshold=0.30):
                            continue  # 相似→目标一致
                        # 不相似→潜在激励冲突
                        results.append({
                            "type": "analytics",
                            "conclusion": f"潜在激励冲突: {s1}({', '.join(f1[:2])})与"
                                          f"{s2}({', '.join(f2[:2])})共享{target}但关注点不同",
                            "derives_from": subjects + [target],
                            "confidence": 0.60,
                        })
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
        team_size, months = 4, 6  # 默认值
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "") + info.get("description", "")
            val = info.get("value", "")
            if "团队" in desc or "合规" in desc:
                team_size = max(1, int(_extract_num(val)))
            if "距" in desc and "月" in desc:
                months = max(1, int(_extract_num(val)))
            if any(kw in desc for kw in ("审计问题", "高风险", "整改率", "认证", "差距")):
                problems.append(f"{desc}={val}")
        if not problems:
            return results

        # 可行性比率 (v3.4): 问题任务数÷(人数×月数)
        task_count = 0
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "")
            val = info.get("value", "")
            if "问题" in desc and _extract_num(val) > 0:
                task_count = max(task_count, int(_extract_num(val)))
        remaining_tasks = max(task_count, 1)
        feasibility = remaining_tasks / max(team_size * months, 1)
        status = "不可行⚠️" if feasibility > 1.5 else ("紧张" if feasibility > 1.0 else "可行")
        results.append({
            "type": "analytics",
            "conclusion": f"整改可行性: {remaining_tasks}问题/{team_size}人/{months}月=人均{feasibility:.1f}个/月→{status}"
                          f"{' 需增加人力或延长时间窗口' if feasibility > 1.0 else ''}",
            "derives_from": [fid for fid, _ in _iter_facts(facts)
                             if any(kw in facts.get(fid, {}).get('desc', '') for kw in ('审计', '整改'))][:5],
            "confidence": 0.85,
        })

        # 严重度分类
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

    # ═══ A6: 市场结构分析 ═══

    def _detect_market_structure(self, facts, entities, relations):
        """检测: 存在实体数量数据+份额分布"""
        n_entities = len(entities) if isinstance(entities, dict) else len(entities)
        return n_entities >= 3

    def _analyze_market_structure(self, facts, entities, relations, enhancer):
        """HHI集中度 + 市场类型判定"""
        results = []
        # 提取实体数量作为市场参与者
        n = len(entities) if isinstance(entities, dict) else len(entities)
        # 从事实中找份额/占比数据
        shares = []
        for fid, info in _iter_facts(facts):
            desc = info.get("desc", "")
            if any(kw in desc for kw in ("份额", "占比", "集中度", "CR")):
                shares.append(_extract_num(info.get("value", "")))
        if not shares:
            return results
        # HHI = sum(share_i^2)
        total = sum(shares) or 1
        hhi = sum((s / total * 100) ** 2 for s in shares)
        mtype = "垄断" if hhi > 2500 else ("寡头" if hhi > 1500 else ("集中" if hhi > 1000 else "分散"))
        cr3 = sum(sorted(shares, reverse=True)[:3]) / total * 100 if len(shares) >= 3 else 100
        results.append({
            "type": "analytics",
            "conclusion": f"市场结构: HHI={hhi:.0f}({mtype}), CR3={cr3:.0f}%, {n}个参与者",
            "derives_from": [fid for fid in facts],
            "confidence": 0.80,
        })
        return results

    # ═══ A7: 博弈均衡检测 ═══

    def _detect_game_equilibrium(self, facts, entities, relations):
        """检测: 多方竞争/合作关系"""
        comp_count = sum(1 for r in (relations or [])
                         if r.get("relation_type") == "competes_with")
        coop_count = sum(1 for r in (relations or [])
                         if r.get("relation_type") == "cooperates_with")
        return comp_count >= 1 or coop_count >= 2

    def _analyze_game_equilibrium(self, facts, entities, relations, enhancer):
        """识别博弈结构: 囚徒困境/协调博弈/零和博弈"""
        results = []
        comps = [r for r in (relations or []) if r.get("relation_type") == "competes_with"]
        coops = [r for r in (relations or []) if r.get("relation_type") == "cooperates_with"]
        # 竞争+合作共存 → 潜在囚徒困境
        if comps and coops:
            results.append({
                "type": "analytics",
                "conclusion": f"囚徒困境风险: {len(comps)}对竞争+{len(coops)}对合作共存, "
                              f"个体理性可能导致集体次优",
                "derives_from": [],
                "confidence": 0.65,
            })
        # 纯竞争 → 零和或负和博弈
        if comps and not coops:
            results.append({
                "type": "analytics",
                "conclusion": f"零和博弈: {len(comps)}对竞争关系, 无合作→可能陷入价格战/军备竞赛",
                "derives_from": [],
                "confidence": 0.70,
            })
        return results

    # ═══ A8: 策略选项生成 ═══

    def _detect_strategic_options(self, facts, entities, relations):
        """检测: 存在问题+约束+资源"""
        has_problem = self._detect_remediation_needed(facts, entities, relations)
        has_constraint = any("约束" in info.get("desc", "") or "限制" in info.get("desc", "")
                             for _, info in _iter_facts(facts))
        return has_problem or has_constraint

    def _analyze_strategic_options(self, facts, entities, relations, enhancer):
        """生成策略选项 — 基于目标/约束/资源组合"""
        results = []
        # 收集目标、约束、资源
        goals = [info.get("desc", "") for _, info in _iter_facts(facts)
                 if any(kw in info.get("desc", "") for kw in ("目标", "计划", "预计"))]
        constraints = [info.get("desc", "") for _, info in _iter_facts(facts)
                       if any(kw in info.get("desc", "") for kw in ("限制", "约束", "上限", "不超过"))]
        resources = [info.get("desc", "") for _, info in _iter_facts(facts)
                     if any(kw in info.get("desc", "") for kw in ("预算", "团队", "储备", "现金"))]
        if not goals and not constraints:
            return results
        # 策略框架
        results.append({
            "type": "analytics",
            "conclusion": f"策略空间: {len(goals)}目标×{len(constraints)}约束×{len(resources)}资源"
                          f"→ 需评估{2**len(goals) if goals else 1}种策略组合",
            "derives_from": [fid for fid in facts],
            "confidence": 0.60,
        })
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
        return 0.0  # bool→0.0 (bool在JSON中不应出现在value字段, 若出现视为0)
    m = re.search(r'(\d+\.?\d*)', str(val))
    return float(m.group(1)) if m else 0.0


def _find_entity_for_fact(fid, desc, entities, matcher=None):
    """根据事实描述找到对应实体ID — 语义匹配优先"""
    if not isinstance(entities, dict):
        return fid
    # TF-IDF语义匹配
    if matcher:
        candidates = [info.get("name", "") for info in entities.values()
                      if isinstance(info, dict)]
        if candidates:
            best, score = matcher.best_match(desc, candidates, threshold=0.15)
            if best and score > 0.15:
                for eid, info in entities.items():
                    if isinstance(info, dict) and info.get("name") == best:
                        return eid
    # 回退: 精确字符串匹配
    for eid, info in entities.items():
        if isinstance(info, dict) and info.get("name", "") in desc:
            return eid
    return fid
