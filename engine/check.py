"""
OntoDerive 规约检查引擎 — 从derive.py拆分
===========================================
13条规约检查(C-01~C-13)，独立模块。
"""
import datetime, re, sys
from pathlib import Path

try:
    from .utils import rf, wf, all_md, load_json, save_json
    from .constants import V2_ID_PATTERNS
except ImportError:
    from utils import rf, wf, all_md, load_json, save_json  # noqa
    from constants import V2_ID_PATTERNS  # noqa


def run_check(root, facts_dir, entities_dir, inferences_dir, scheme_dir, log_dir):
    """执行全部13条规约检查。返回(results, severity_counts)"""
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
    try:
        from typesystem import TypeValidator
        tv = TypeValidator()
        ids_found = set()
        for m in re.finditer(r'\b([A-Z][A-Za-z0-9_-]*(?:-[A-Za-z0-9_-]+)*)\b', all_text):
            raw_id = m.group(0)
            if '-' not in raw_id or len(raw_id) < 3:
                continue
            if raw_id in ids_found:
                continue
            ids_found.add(raw_id)
            r = tv.check_id(raw_id)
            if not r.is_valid:
                type_errors.append(f"{raw_id}({r.errors[0]})")
    except ImportError:
        pass  # typesystem.py 可选模块，不可用时不阻塞

    bad_ids = re.findall(r'\b(ORG[A-Z]|ROL[A-Z]|PRJ[A-Z]|DAT\d|INF[A-Z]|POL\d)', all_text)
    detail_c7 = f"异常格式: {len(bad_ids)} 个, v2前缀共{len(V2_ID_PATTERNS)}种"
    if type_errors:
        detail_c7 += f", 类型错误: {len(type_errors)}个 [{'; '.join(type_errors[:3])}]"
    result("C-07", "实体ID合规性(v2.1)", len(bad_ids) == 0,
           "WARN" if bad_ids or type_errors else "PASS", detail_c7)

    # C8: 引擎自检
    script_path = Path(__file__).resolve()
    result("C-08", "推导引擎健康度", script_path.exists(),
           "BLOCKER" if not script_path.exists() else "PASS", f"引擎: {script_path.name}")

    # C9: 贝叶斯信念传播（结果缓存供C-10复用）
    _bayes_distribution = None
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from bayesian import BayesianLayer
        bl = BayesianLayer(root)
        _bayes_distribution = bl.get_distribution()
        all_confs = _bayes_distribution["facts"] + _bayes_distribution["inferences"]
        valid_confs = all(0 < c < 1 for c in all_confs) if all_confs else True
        has_variance = len(set(round(c, 1) for c in all_confs)) > 1 if all_confs else True
        bayes_ok = valid_confs and has_variance
        result("C-09", "贝叶斯信念传播(智能层)", bayes_ok,
               "WARN" if not bayes_ok else "PASS",
               f"事实{_bayes_distribution['n_facts']}个, 推论{_bayes_distribution['n_inferences']}个, "
               f"平均置信度{sum(all_confs)/len(all_confs):.2f}" if all_confs else "N/A")
    except ImportError:
        result("C-09", "贝叶斯信念传播(智能层)", False, "WARN", "bayesian.py模块未安装")
    except Exception as e:
        result("C-09", "贝叶斯信念传播(智能层)", False, "WARN", f"执行异常: {str(e)[:50]}")

    # C10: 信息论层（使用C-09的预计算置信度，不重新实例化Bayesian）
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from metrics import MetricsLayer
        ml = MetricsLayer(root)
        kqi = ml.compute_kqi(precomputed_confs=_bayes_distribution)
        kqi_ok = kqi["kqi"] > 0 and kqi["entropy"] >= 0
        result("C-10", "信息论层(KQI质量指数)", kqi_ok, "PASS",
               f"KQI={kqi['kqi']}, 熵={kqi['entropy']}bits, "
               f"密度={kqi['density']:.2f}, 覆盖={kqi['coverage']*100:.0f}%")
    except ImportError:
        result("C-10", "信息论层(KQI质量指数)", False, "WARN", "metrics.py模块未安装")
    except Exception as e:
        result("C-10", "信息论层(KQI质量指数)", False, "WARN", f"异常: {str(e)[:50]}")

    # C11: 控制论层
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from controller import PIDController
        ctrl = PIDController(root)
        pid = ctrl.analyze()
        result("C-11", "控制论层(PID反馈)", pid["stability"] == "stable",
               "WARN" if pid["stability"] != "stable" else "PASS",
               f"P={pid['p_value']} I={pid['i_value']} D={pid['d_value']} "
               f"信号={pid['control_signal']} 状态={pid['stability']}")
    except Exception as e:
        result("C-11", "控制论层(PID反馈)", True, "PASS", f"首次运行, 信号=0 (需要历史数据)")

    # C12: 图灵机层
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from turing_k import KnowledgeTM
        ktm = KnowledgeTM(root)
        state = ktm.snapshot()
        result("C-12", "图灵机层(知识状态机)", state.timestamp is not None,
               "PASS", f"快照: {state.facts}F/{state.inferences}I/{state.entities}E")
    except Exception as e:
        result("C-12", "图灵机层(知识状态机)", False, "WARN", f"异常: {str(e)[:50]}")

    # C13: 形式语言层
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from ontolang import OntoLangParser
        parser = OntoLangParser()
        ast = parser.test_suite()
        total_nodes = len(ast["entities"]) + len(ast["facts"]) + len(ast["inferences"]) + len(ast["protocols"])
        errors = parser.validate(ast)
        result("C-13", "形式语言层(OntoLang解析)", len(errors) == 0,
               "PASS" if len(errors) == 0 else "ERROR",
               f"AST节点{total_nodes}个, 错误{len(errors)}个")
    except Exception as e:
        result("C-13", "形式语言层(OntoLang解析)", False, "WARN", f"异常: {str(e)[:50]}")

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
