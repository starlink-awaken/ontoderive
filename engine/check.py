"""
OntoDerive 规约检查引擎 — 从derive.py拆分
===========================================
13条规约检查(C-01~C-13)，独立模块。
"""
import datetime, re
from pathlib import Path

try:
    from .utils import CachedReader, save_json
    from .constants import V2_ID_PATTERNS
except ImportError:
    from utils import CachedReader, save_json  # noqa
    from constants import V2_ID_PATTERNS  # noqa


def run_check(root, facts_dir, entities_dir, inferences_dir, scheme_dir, log_dir):
    """执行全部13条规约检查，使用CachedReader消除重复I/O"""
    cr = CachedReader()
    rf, all_md = cr.rf, cr.all_md
    results = []
    severity_counts = {"PASS": 0, "WARN": 0, "ERROR": 0, "BLOCKER": 0}

    def result(pid, name, passed, severity, detail, fixes=None, file="", line=0):
        r = {"protocol_id": pid, "name": name, "passed": passed,
             "severity": severity, "detail": detail, "fixes": fixes or [],
             "file": file, "line": line}
        results.append(r)
        cat = "PASS" if passed else severity
        severity_counts[cat] = severity_counts.get(cat, 0) + 1
        icon = {"PASS": "✅", "WARN": "🟡", "ERROR": "🟠", "BLOCKER": "🔴"}.get(cat, "⚪")
        print(f"  {icon} [{severity}] {pid} — {detail[:80]}")
        return r

    # C1-C3: 文件存在性
    facts_exist = len(all_md(facts_dir)) > 0
    result("C-01", "事实基座完整性", facts_exist, "BLOCKER" if not facts_exist else "PASS",
           f"事实文件: {len(all_md(facts_dir))} 个", ["创建 facts/data.md 和 facts/policy.md"])

    infs_exist = len(all_md(inferences_dir)) > 0
    result("C-02", "推论体系完整性", infs_exist, "ERROR" if not infs_exist else "PASS",
           f"推论文件: {len(all_md(inferences_dir))} 个", ["创建 inferences/contradictions.md"])

    schemes = all_md(scheme_dir)
    result("C-03", "方案文件完整性", len(schemes) > 0, "ERROR" if len(schemes) == 0 else "PASS",
           f"方案文件: {len(schemes)} 个")

    # C4: 事实编号追溯
    fact_ids = set()
    for f in all_md(facts_dir):
        text = rf(f)
        fact_ids.update(re.findall(r'(D-F\d+|P-F\d+)', text))

    inf_text = ""
    for f in all_md(inferences_dir):
        inf_text += rf(f)
    scheme_text = ""
    for f in schemes:
        scheme_text += rf(f)

    traced_in_inf = sum(1 for fid in fact_ids if fid in inf_text)
    traced_in_scheme = sum(1 for fid in fact_ids if fid in scheme_text)
    untraced = [fid for fid in fact_ids if fid not in scheme_text]
    detail_c4 = f"事实{len(fact_ids)}个: 推论引用{traced_in_inf}, 方案引用{traced_in_scheme}"
    # v2.3: 蕴含图运行时统计
    try:
        from logic import build_from_project
        g = build_from_project(root)
        gs = g.stats()
        detail_c4 += f" | 蕴含图: {gs['nodes']}节点/{gs['edges']}边, 深度{gs['max_depth']}"
    except Exception:
        pass
    if untraced:
        detail_c4 += f", 未追溯{len(untraced)}个: {','.join(untraced[:3])}"
    result("C-04", "事实可追溯性", traced_in_inf > 0 and traced_in_scheme > 0,
           "WARN" if traced_in_inf == 0 else "PASS", detail_c4, ["标注事实编号引用"])

    # C5: 断言可追溯性（含file:line）
    total_assertions = 0
    traced_assertions = 0
    untraced_assertions = []
    for doc in schemes:
        text = rf(doc)
        rel_path = str(doc.relative_to(root))
        text_clean = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text_clean = re.sub(r'^#+\s+.*$', '', text_clean, flags=re.MULTILINE)
        for line_no, line in enumerate(text_clean.split('\n'), 1):
            assertions = re.findall(r'[^。\n]*?(?:应该|必须|需要)[^。]*?[。]', line)
            for a in assertions:
                if len(a) < 15:
                    continue
                total_assertions += 1
                if re.search(r'D-F\d+|P-F\d+|INF-|INF-V2-', a):
                    traced_assertions += 1
                else:
                    untraced_assertions.append(f"{rel_path}:{line_no}")
    rate = (traced_assertions / total_assertions * 100) if total_assertions > 0 else 100
    detail_c5 = f"断言{total_assertions}个, 可追溯{traced_assertions}, 率{rate:.0f}%"
    if untraced_assertions:
        detail_c5 += f", 未追溯: {untraced_assertions[0]}..."
    result("C-05", "断言可追溯性", rate >= 30,
           "WARN" if rate < 50 else ("ERROR" if rate < 30 else "PASS"), detail_c5,
           ["在含'应该/必须/需要'的句子旁标注事实编号引用"])

    # C6: 关键判断可证伪性（含file:line）
    falsifiable_total = 0
    falsifiable_ok = 0
    non_falsifiable = []
    for doc in schemes:
        text = rf(doc)
        rel_path = str(doc.relative_to(root))
        lines = text.split('\n')
        for line_no, line in enumerate(lines, 1):
            claims = re.findall(
                r'[^。]*(?:投入|产出|营收|建成|上线|完成|达到|成本|利润|转化率)[^。]*?(?:万|亿|年|月|日|%|倍)[^。]*。',
                line)
            for c in claims:
                falsifiable_total += 1
                ctx = text[max(0, text.find(c)-100):text.find(c)+len(c)+100] if c in text else c
                if re.search(r'如果.*?则|若.*?则|假设|条件|除非', ctx):
                    falsifiable_ok += 1
                else:
                    non_falsifiable.append(f"{rel_path}:{line_no}")
    rate_f = (falsifiable_ok / falsifiable_total * 100) if falsifiable_total > 0 else 100
    detail_c6 = f"预测断言{falsifiable_total}个, 可证伪{falsifiable_ok}, 率{rate_f:.0f}%"
    if non_falsifiable:
        detail_c6 += f", 不可证伪: {non_falsifiable[0]}..."
    result("C-06", "关键判断可证伪性", rate_f >= 15,
           "WARN" if rate_f < 30 else "PASS", detail_c6,
           ["为核心数字断言添加'如果X月后Y没发生则重新评估'条件"])

    # C7: 实体ID合规性（v2.1: 使用TypeValidator）
    all_text = ""
    for d in [facts_dir, entities_dir, inferences_dir, scheme_dir]:
        for f in all_md(d):
            all_text += rf(f)

    type_errors = []
    ids_found = set()
    SKIP_PREFIXES = ("C-", "P-", "ISC-", "F", "v", "v2", "v3", "E", "e")
    try:
        from typesystem import TypeValidator
        tv = TypeValidator()
        for m in re.finditer(r'\b([A-Z][A-Za-z0-9_-]*(?:-[A-Za-z0-9_-]+)*)\b', all_text):
            raw_id = m.group(0)
            if '-' not in raw_id or len(raw_id) < 3:
                continue
            if any(raw_id.startswith(p) for p in SKIP_PREFIXES):
                continue
            if raw_id in ids_found:
                continue
            ids_found.add(raw_id)
            r = tv.check_id(raw_id)
            if not r.is_valid:
                type_errors.append(f"{raw_id}({r.errors[0]})")
    except ImportError:
        pass

    detail_c7 = f"v2前缀{len(V2_ID_PATTERNS)}种"
    if type_errors:
        detail_c7 += f", 类型错误: {len(type_errors)}个 [{'; '.join(type_errors[:3])}]"
    elif len(ids_found) > 0:
        detail_c7 += f", 校验通过: {len(ids_found)}个ID"
    result("C-07", "实体ID合规性(v2.2 TypeValidator)", len(type_errors) == 0,
           "WARN" if type_errors else "PASS", detail_c7)

    # C8: 引擎自检
    script_path = Path(__file__).resolve()
    result("C-08", "推导引擎健康度", script_path.exists(),
           "BLOCKER" if not script_path.exists() else "PASS", f"引擎: {script_path.name}")

    # C9~C13: 委theory_check_registry（策略模式解耦）
    try:
        from .check_theory import THEORY_CHECKS, check_bayesian
    except ImportError:
        from check_theory import THEORY_CHECKS, check_bayesian  # noqa

    # C9: 贝叶斯 → 结果缓存供C-10复用
    try:
        r9 = check_bayesian(root)
        result("C-09", r9["name"] if "name" in r9 else "贝叶斯信念传播(智能层)",
               r9["passed"], r9["severity"], r9["detail"])
        _bayes_distribution = r9.get("distribution")
    except Exception as e:
        result("C-09", "贝叶斯信念传播(智能层)", False, "WARN", str(e)[:50])
        _bayes_distribution = None

    # C10~C13: 通过注册表调用，而非直接import
    for pid, name, check_fn in THEORY_CHECKS:
        if pid == "C-09":
            continue  # 已在上面处理（需要缓存distribution）
        try:
            kwargs = {}
            if pid == "C-10" and _bayes_distribution:
                kwargs["precomputed_confs"] = _bayes_distribution
            r = check_fn(root, **kwargs) if pid == "C-10" else check_fn(root)
            result(pid, name, r["passed"], r["severity"], r["detail"])
        except Exception as e:
            result(pid, name, False, "WARN", f"异常: {str(e)[:50]}")

    # 保存结果
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    save_json(log_dir / f"check-result-{ts}.json",
             {"checked_at": datetime.datetime.now().isoformat(),
              "total": len(results), "passed": severity_counts["PASS"],
              "severities": severity_counts, "details": results})
    save_json(log_dir / "check-result.json",
             {"checked_at": datetime.datetime.now().isoformat(),
              "total": len(results), "passed": severity_counts["PASS"],
              "severities": severity_counts, "details": results})

    total = len(results)
    passed_count = severity_counts["PASS"]
    print(f"[check] 📊 规约检查: {passed_count}/{total} 通过"
          f" (BLOCKER={severity_counts['BLOCKER']}"
          f" ERROR={severity_counts['ERROR']}"
          f" WARN={severity_counts['WARN']})")

    return results, severity_counts
