"""Analysis patterns"""

import re

from engine.foundation.semantic import SemanticMatcher

from .analytics_constants import (
    _DISRUPTION_KW,
    _HISTORY_KW,
    _INERTIA_KW,
    _MARKET_KW,
    _RESOURCE_KW,
    _TECH_NEW_KW,
    _TECH_OLD_KW,
)

# Helpers
#############################################

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
    m = re.search(r"(\d+\.?\d*)", str(val))
    return float(m.group(1)) if m else 0.0


def _find_entity_for_fact(fid, desc, entities, matcher=None):
    """根据事实描述找到对应实体ID — 语义匹配优先"""
    if not isinstance(entities, dict):
        return fid
    # TF-IDF语义匹配
    if matcher:
        candidates = [info.get("name", "") for info in entities.values() if isinstance(info, dict)]
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


# Pattern functions
#############################################

def detect_capacity_constraint(engine, facts, entities, relations):
    """检测: 利用率>90%供给紧张 或 利用率<60%产能过剩 或 库存偏离基准"""
    for fid, info in _iter_facts(facts):
        desc = info.get("desc", "") + info.get("description", "")
        val = info.get("value", "")
        if "利用率" in desc or "产能" in desc:
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


def analyze_capacity(engine, facts, entities, relations, enhancer):
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
            results.append(
                {
                    "type": "analytics",
                    "conclusion": f"供给弹性≈{elasticity:.2f}: '{desc}'={val}, "
                    f"仅余{100 - num:.0f}%产能, 需求波动将直接传导为短缺",
                    "derives_from": [fid],
                    "confidence": 0.85,
                }
            )
        # 产能过剩检测 (v3.4)
        elif "利用率" in desc and num > 0 and num < 60:
            excess_pct = 100 - num
            results.append(
                {
                    "type": "analytics",
                    "conclusion": f"产能过剩: '{desc}'={val}, 闲置{excess_pct:.0f}%产能, "
                    f"供过于求→价格下行→行业出清压力",
                    "derives_from": [fid],
                    "confidence": 0.80,
                }
            )
        # 库存vs安全基准
        if "库存" in desc:
            for fid2, info2 in _iter_facts(facts):
                if "安全" in info2.get("desc", ""):
                    safe = _extract_num(info2.get("value", ""))
                    if safe > num:
                        gap_pct = (safe - num) / safe * 100
                        results.append(
                            {
                                "type": "analytics",
                                "conclusion": f"库存缺口: '{desc}'={val}低于安全基准{safe}, "
                                f"缺口{gap_pct:.0f}%, 补库压力紧迫",
                                "derives_from": [fid, fid2],
                                "confidence": 0.90,
                            }
                        )
    return results

# ═══ A2: 供应链风险放大 ═══


def detect_supply_risk(engine, facts, entities, relations):
    """检测: 存在depends_on链 + 交付/库存异常"""
    has_chain = any(r.get("relation_type") == "depends_on" for r in (relations or []))
    has_issue = any(
        "交付" in (f.get("desc", "") + f.get("description", "")) and _extract_num(f.get("value", "")) < 80
        for _, f in _iter_facts(facts)
    )
    return has_chain and has_issue


def analyze_supply_chain(engine, facts, entities, relations, enhancer):
    results = []
    # 语义匹配器: 基于事实描述
    descs = [info.get("desc", "") for _, info in _iter_facts(facts)]
    matcher = SemanticMatcher(descs if descs else ["default"])
    # 构建依赖图
    deps = {}
    for r in relations or []:
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
                    results.append(
                        {
                            "type": "analytics",
                            "conclusion": f"风险传导: {entity_name}交付{delivery}%→上游{up_name}"
                            f"库存{stock}天, 放大系数≈{amplification:.2f}",
                            "derives_from": [fid, fid2],
                            "confidence": 0.75,
                        }
                    )
    return results

# ═══ A3: 代理问题 ═══


def detect_agency_issue(engine, facts, entities, relations):
    """检测: X employs Y, 且Y的工作输出实际服务于Z(≠X)"""
    employs_pairs = [(r["subject"], r["object"]) for r in (relations or []) if r.get("relation_type") == "employs"]
    if not employs_pairs:
        return False
    # 检查被雇佣方是否通过其他关系服务于第三方
    for employer, employee in employs_pairs:
        for r in relations or []:
            if (
                r.get("subject") == employee
                and r.get("relation_type") in ("cooperates_with", "depends_on", "influences")
                and r.get("object") != employer
            ):
                return True
    return False


def analyze_agency(engine, facts, entities, relations, enhancer):
    results = []
    employs_pairs = [(r["subject"], r["object"]) for r in (relations or []) if r.get("relation_type") == "employs"]
    for employer, employee in employs_pairs:
        for r in relations or []:
            if r.get("subject") == employee and r.get("object") != employer:
                base = (
                    f"潜在代理问题: {employer} employs {employee}, "
                    f"但{employee}的'{r['relation_type']}'关系指向{r['object']}"
                )
                if enhancer and enhancer.available:
                    try:
                        enhanced = enhancer._call(
                            f"分析以下代理问题的组织影响(一句话): {base}", "你是组织行为学专家。", 0.3
                        )
                        if enhanced:
                            base += f"。LLM分析: {enhanced.strip()[:200]}"
                    except Exception:
                        pass
                results.append(
                    {
                        "type": "analytics",
                        "conclusion": base,
                        "derives_from": [employer, employee, r.get("object", "")],
                        "confidence": 0.70,
                    }
                )
    return results

# ═══ A4: 激励不相容 ═══


def detect_incentive_issue(engine, facts, entities, relations):
    """检测: 多实体共享资源(语义关联) + 有不同的事实描述"""
    # 找共享同一目标实体的多个主体
    targets = {}
    for r in relations or []:
        obj = r.get("object", "")
        targets.setdefault(obj, []).append(r.get("subject", ""))
    shared_resources = [(t, subs) for t, subs in targets.items() if len(subs) >= 2]
    return len(shared_resources) >= 1


def analyze_incentive(engine, facts, entities, relations, enhancer):
    results = []
    # 匹配器: 用事实描述语料
    fact_desc = [f.get("desc", "") for f in facts.values() if isinstance(f, dict)]
    matcher = SemanticMatcher(fact_desc if fact_desc else ["default"])

    targets = {}
    for r in relations or []:
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
                    results.append(
                        {
                            "type": "analytics",
                            "conclusion": f"潜在激励冲突: {s1}({', '.join(f1[:2])})与"
                            f"{s2}({', '.join(f2[:2])})共享{target}但关注点不同",
                            "derives_from": subjects + [target],
                            "confidence": 0.60,
                        }
                    )
    return results

# ═══ A5: 补救规划 ═══


def detect_remediation_needed(engine, facts, entities, relations):
    """检测: 存在'问题'/'审计'/'整改'相关事实或推论"""
    for _, info in _iter_facts(facts):
        desc = info.get("desc", "") + info.get("description", "")
        if any(kw in desc for kw in ("审计", "整改", "问题", "风险", "违规", "差距")):
            return True
    return False


def analyze_remediation(engine, facts, entities, relations, enhancer):
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
    results.append(
        {
            "type": "analytics",
            "conclusion": (
                f"整改可行性: {remaining_tasks}问题/{team_size}人/{months}月="
                f"人均{feasibility:.1f}个/月→{status}"
                f"{' 需增加人力或延长时间窗口' if feasibility > 1.0 else ''}"
            ),
            "derives_from": [
                fid
                for fid, _ in _iter_facts(facts)
                if any(kw in facts.get(fid, {}).get("desc", "") for kw in ("审计", "整改"))
            ][:5],
            "confidence": 0.85,
        }
    )

    # 严重度分类
    high_risk = sum(1 for p in problems if "高风险" in p or "差距" in p)
    if high_risk > 0:
        results.append(
            {
                "type": "analytics",
                "conclusion": f"短期(0-3月)优先: 解决{high_risk}个高风险项, 防止监管执法触发",
                "derives_from": [fid for fid in facts],
                "confidence": 0.80,
            }
        )

    if enhancer and enhancer.available:
        try:
            context = "; ".join(problems[:8])
            plan = enhancer._call(
                f"基于以下问题生成分阶段补救方案(短/中/长期各1-2句话): {context}", "你是战略规划专家。", 0.4
            )
            if plan:
                results.append(
                    {
                        "type": "analytics",
                        "conclusion": f"分阶段方案: {plan.strip()[:300]}",
                        "derives_from": [
                            fid
                            for fid in facts
                            if any(kw in facts[fid].get("desc", "") for kw in ("审计", "整改", "问题"))
                        ],
                        "confidence": 0.65,
                    }
                )
        except Exception:
            pass
    return results

# ═══ A6: 市场结构分析 ═══


def detect_market_structure(engine, facts, entities, relations):
    """检测: ≥3实体 或 存在市场份额关键词"""
    n_entities = len(entities) if isinstance(entities, dict) else len(entities)
    if n_entities >= 3:
        return True
    for _, info in _iter_facts(facts):
        if any(kw in info.get("desc", "") for kw in _MARKET_KW):
            return True
    return False


def analyze_market_structure(engine, facts, entities, relations, enhancer):
    """HHI集中度 + 市场类型判定"""
    results = []
    n = len(entities) if isinstance(entities, dict) else len(entities)
    shares = []
    for fid, info in _iter_facts(facts):
        desc = info.get("desc", "")
        if any(kw in desc for kw in _MARKET_KW):
            shares.append(_extract_num(info.get("value", "")))
    if not shares:
        return results
    # HHI = sum(share_i^2)
    total = sum(shares) or 1
    hhi = sum((s / total * 100) ** 2 for s in shares)
    mtype = "垄断" if hhi > 2500 else ("寡头" if hhi > 1500 else ("集中" if hhi > 1000 else "分散"))
    cr3 = sum(sorted(shares, reverse=True)[:3]) / total * 100 if len(shares) >= 3 else 100
    results.append(
        {
            "type": "analytics",
            "conclusion": f"市场结构: HHI={hhi:.0f}({mtype}), CR3={cr3:.0f}%, {n}个参与者",
            "derives_from": [fid for fid in facts],
            "confidence": 0.80,
        }
    )
    return results

# ═══ A7: 博弈均衡检测 ═══


def detect_game_equilibrium(engine, facts, entities, relations):
    """检测: 多方竞争/合作关系"""
    comp_count = sum(1 for r in (relations or []) if r.get("relation_type") == "competes_with")
    coop_count = sum(1 for r in (relations or []) if r.get("relation_type") == "cooperates_with")
    return comp_count >= 1 or coop_count >= 2


def analyze_game_equilibrium(engine, facts, entities, relations, enhancer):
    """识别博弈结构: 囚徒困境/协调博弈/零和博弈"""
    results = []
    comps = [r for r in (relations or []) if r.get("relation_type") == "competes_with"]
    coops = [r for r in (relations or []) if r.get("relation_type") == "cooperates_with"]
    # 竞争+合作共存 → 潜在囚徒困境
    if comps and coops:
        results.append(
            {
                "type": "analytics",
                "conclusion": f"囚徒困境风险: {len(comps)}对竞争+{len(coops)}对合作共存, 个体理性可能导致集体次优",
                "derives_from": [],
                "confidence": 0.65,
            }
        )
    # 纯竞争 → 零和或负和博弈
    if comps and not coops:
        results.append(
            {
                "type": "analytics",
                "conclusion": f"零和博弈: {len(comps)}对竞争关系, 无合作→可能陷入价格战/军备竞赛",
                "derives_from": [],
                "confidence": 0.70,
            }
        )
    return results

# ═══ A8: 策略选项生成 ═══


def detect_strategic_options(engine, facts, entities, relations):
    """检测: 存在问题+约束+资源"""
    has_problem = detect_remediation_needed(engine, facts, entities, relations)
    has_constraint = any(
        "约束" in info.get("desc", "") or "限制" in info.get("desc", "") for _, info in _iter_facts(facts)
    )
    return has_problem or has_constraint


def analyze_strategic_options(engine, facts, entities, relations, enhancer):
    """生成策略选项 — 基于目标/约束/资源组合"""
    results = []
    # 收集目标、约束、资源
    goals = [
        info.get("desc", "")
        for _, info in _iter_facts(facts)
        if any(kw in info.get("desc", "") for kw in ("目标", "计划", "预计"))
    ]
    constraints = [
        info.get("desc", "")
        for _, info in _iter_facts(facts)
        if any(kw in info.get("desc", "") for kw in ("限制", "约束", "上限", "不超过"))
    ]
    resources = [
        info.get("desc", "")
        for _, info in _iter_facts(facts)
        if any(kw in info.get("desc", "") for kw in ("预算", "团队", "储备", "现金"))
    ]
    if not goals and not constraints:
        return results
    # 策略空间 + 帕累托分析
    n_combos = 2 ** len(goals) if goals else 1
    feasible = max(1, n_combos - len(constraints))
    pareto_note = ""
    tree_depth = len(goals) + len(constraints)
    if len(goals) >= 2 and len(constraints) >= 1:
        pareto_note = f", 约束{len(constraints)}个→帕累托前沿需在{feasible}个可行解中寻找"
    depth_str = f", 博弈树深度≈{tree_depth}" if goals else ""
    results.append(
        {
            "type": "analytics",
            "conclusion": f"策略空间: {len(goals)}目标×{len(constraints)}约束×{len(resources)}资源"
            f"→ {n_combos}种组合{depth_str}{pareto_note}",
            "derives_from": [fid for fid in facts],
            "confidence": 0.60,
        }
    )
    return results

# ═══ A9: 信息生态健康度 (v3.5) ═══


def detect_info_ecology(engine, facts, entities, relations):
    """检测: 虚假信息/可信度/信任度/共识度相关数据"""
    kw = ("虚假信息", "可信度", "信任度", "共识度", "信息", "公众信任")
    for _, info in _iter_facts(facts):
        if any(k in info.get("desc", "") for k in kw):
            return True
    return False


def analyze_info_ecology(engine, facts, entities, relations, enhancer):
    """信息生态健康度评分"""
    results = []
    disinfo = trust = consensus = 0.0
    for _, info in _iter_facts(facts):
        desc = info.get("desc", "")
        val = _extract_num(info.get("value", ""))
        if "虚假" in desc:
            disinfo = val
        elif "信任" in desc and val > 0:
            trust = val
        elif "共识" in desc and val > 0:
            consensus = val
    if not (disinfo or trust or consensus):
        return results
    # 信息生态健康度 = (1 - 虚假率) × 信任度 × 共识度归一化
    health = (100 - disinfo) / 100 * (trust / 100) * (consensus / 100) * 100
    status = "崩溃" if health < 5 else ("危机" if health < 15 else ("脆弱" if health < 30 else "健康"))
    results.append(
        {
            "type": "analytics",
            "conclusion": f"信息生态健康度: {health:.1f}/100({status}), "
            f"虚假{disinfo}%+信任{trust}%+共识{consensus}%→"
            f"{'事实共识已瓦解' if health < 15 else '尚可正常决策'}",
            "derives_from": [],
            "confidence": 0.75,
        }
    )
    return results

# ═══ A10: 因果链分析 (v3.6) ═══


def detect_causal_chain(engine, facts, entities, relations):
    return len(relations or []) >= 1


def analyze_causal_chain(engine, facts, entities, relations, enhancer):
    results = []
    deps = {}
    for r in relations or []:
        if r.get("relation_type") in ("depends_on", "causes", "influences"):
            deps.setdefault(r["subject"], []).append(r["object"])
    if len(deps) < 2:
        return results
    # BFS找所有因果路径 (v3.6 fix: 多分支)
    for start in deps:
        paths = [[start]]
        for path in paths:
            last = path[-1]
            if last in deps:
                for up in deps[last]:
                    if up not in path:
                        new_path = path + [up]
                        paths.append(new_path)
                        if len(new_path) >= 3:
                            results.append(
                                {
                                    "type": "analytics",
                                    "conclusion": f"因果链: {'→'.join(new_path)}, "
                                    f"深度{len(new_path) - 1}, "
                                    f"中介{new_path[1:-1]}, 根因={new_path[-1]}",
                                    "derives_from": new_path[:3],
                                    "confidence": 0.75,
                                }
                            )
    return results

# ═══ A11: 情景规划 (v3.6) ═══


def detect_scenario_planning(engine, facts, entities, relations):
    kw = ("不确定性", "概率", "情景", "乐观", "悲观", "基线", "可能")
    for _, info in _iter_facts(facts):
        if any(k in info.get("desc", "") for k in kw):
            return True
    return False


def analyze_scenario_planning(engine, facts, entities, relations, enhancer):
    results = []
    uncertainties = []
    for _, info in _iter_facts(facts):
        desc = info.get("desc", "")
        val = info.get("value", "")
        if any(k in desc for k in ("不确定性", "概率", "风险")):
            uncertainties.append((desc, _extract_num(val)))
    if len(uncertainties) < 2:
        return results
    u1, u2 = uncertainties[:2]
    scenarios = [
        (f"{u1[0]}高+{u2[0]}高", "乐观"),
        (f"{u1[0]}高+{u2[0]}低", "基准偏上"),
        (f"{u1[0]}低+{u2[0]}高", "基准偏下"),
        (f"{u1[0]}低+{u2[0]}低", "悲观"),
    ]
    results.append(
        {
            "type": "analytics",
            "conclusion": f"情景矩阵(2×2): {len(scenarios)}情景, "
            f"关键轴={u1[0]}({u1[1]:.0f})×{u2[0]}({u2[1]:.0f}), "
            f"早鸟指标: {u1[0]}趋势逆转或{u2[0]}突破阈值",
            "derives_from": [],
            "confidence": 0.60,
        }
    )
    return results

# ═══ A12: 权力地图 (v3.6) ═══


def detect_power_map(engine, facts, entities, relations):
    return len(relations or []) >= 4


def analyze_power_map(engine, facts, entities, relations, enhancer):
    results = []
    # Degree centrality (度中心性): 每个节点参与的关系数
    centrality = {}
    for r in relations or []:
        s, o = r.get("subject", ""), r.get("object", "")
        centrality[s] = centrality.get(s, 0) + 1
        centrality[o] = centrality.get(o, 0) + 1
    if not centrality:
        return results
    top = sorted(centrality.items(), key=lambda x: -x[1])[:3]
    results.append(
        {
            "type": "analytics",
            "conclusion": f"权力地图: 关键节点={', '.join(f'{k}(度={v})' for k, v in top)}, "
            f"最大影响力={top[0][0]}({top[0][1]}连接), "
            f"潜在单点={'是' if top[0][1] >= len(centrality) / 2 else '否'}",
            "derives_from": [k for k, _ in top],
            "confidence": 0.70,
        }
    )
    return results

# ═══ A13: 组织惯性分析 (v3.6) ═══


def detect_organizational_inertia(engine, facts, entities, relations):
    """检测: 规模大/历史悠久/投入多 + 转型慢/变化难/惯性/路径依赖"""
    if len(entities or {}) >= 3 or len(relations or []) >= 4:
        return True
    for _, info in _iter_facts(facts):
        if any(k in info.get("desc", "") for k in _INERTIA_KW):
            return True
    return False


def analyze_organizational_inertia(engine, facts, entities, relations, enhancer):
    results = []
    if not entities:
        return results

    entity_count = len(entities or {})
    relation_count = len(relations or [])
    complexity = relation_count / max(entity_count, 1)

    history_signals = 0
    resource_lock = 0
    for _, info in _iter_facts(facts):
        desc = info.get("desc", "")
        if any(k in desc for k in _HISTORY_KW):
            history_signals += 1
        if any(k in desc for k in _RESOURCE_KW):
            resource_lock += 1

    inertia_index = complexity * (1 + history_signals) * (1 + resource_lock)
    level = "高" if inertia_index >= 6 else ("中" if inertia_index >= 3 else "低")

    top_entities = sorted(
        [eid for eid in (entities or {})],
        key=lambda e: sum(1 for r in (relations or []) if r.get("subject") == e or r.get("object") == e),
        reverse=True,
    )[:3]

    results.append(
        {
            "type": "analytics",
            "conclusion": f"组织惯性: 指数={inertia_index:.1f}({level}), "
            f"{entity_count}实体/{relation_count}关系, "
            f"复杂度={complexity:.1f}, "
            f"历史信号={history_signals}, 资源锁定={resource_lock}",
            "derives_from": top_entities,
            "confidence": 0.65,
        }
    )
    return results

# ═══ A14: 技术颠覆风险 (v3.6) ═══


def detect_tech_disruption(engine, facts, entities, relations):
    """检测: 新技术信号 + 传统技术描述"""
    has_new = False
    has_old = False
    for _, info in _iter_facts(facts):
        desc = info.get("desc", "")
        if any(k in desc for k in _DISRUPTION_KW):
            return True
        if any(k in desc for k in _TECH_NEW_KW):
            has_new = True
        if any(k in desc for k in _TECH_OLD_KW):
            has_old = True
    return has_new or has_old


def analyze_tech_disruption(engine, facts, entities, relations, enhancer):
    results = []

    new_signals = 0
    old_lock = 0
    new_entities = []
    old_entities = []
    for fid, info in _iter_facts(facts):
        desc = info.get("desc", "")
        new_signals += sum(1 for k in _TECH_NEW_KW if k in desc)
        old_lock += sum(1 for k in _TECH_OLD_KW if k in desc)
        if any(k in desc for k in _TECH_NEW_KW):
            new_entities.append(fid)
        if any(k in desc for k in _TECH_OLD_KW):
            old_entities.append(fid)

    disruption_pressure = new_signals / max(old_lock, 1)
    threat_level = "高" if disruption_pressure >= 2 else ("中" if disruption_pressure >= 1 else "低")

    conclusion = (
        f"技术颠覆风险: 压力={disruption_pressure:.1f}({threat_level}), "
        f"新技术信号={new_signals}, 现有锁定={old_lock}, "
    )
    if threat_level == "高":
        conclusion += "警告: 新技术威胁显著, 建议制定转型路线图"
    elif threat_level == "中":
        conclusion += "关注: 新技术正在积累, 建议跟踪监测"
    else:
        conclusion += "正常: 现有技术仍占主导"

    results.append(
        {
            "type": "analytics",
            "conclusion": conclusion,
            "derives_from": new_entities[:3] + old_entities[:3],
            "confidence": 0.70,
        }
    )
    return results


