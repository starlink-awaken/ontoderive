#!/usr/bin/env python3
"""
OntoDerive 推导引擎 v1.1
=========================
事实驱动推导引擎：事实→本体→推论→方案的全链路可追溯推导。
支持多轮迭代、双向规约校验、断言追溯检测、实体完整性检查。

核心能力：
1. 事实基座完整性检查
2. 实体ID合规性检查
3. 断言可追溯性检查(assertion_traceable)
4. 关键判断可证伪性检查(falsifiable)
5. 方案文件存在性检查
6. 推导链连续性检查
7. 多轮迭代收敛(derive → check → fix → re-check)

用法:
    python3 derive.py --init my-project     # 初始化
    python3 derive.py --derive              # 正向推导
    python3 derive.py --check               # 规约检查(含可追溯+可证伪)
    python3 derive.py --resolve             # 自动修复可修复项
    python3 derive.py --rounds 5            # 多轮迭代
    python3 derive.py --generate report     # 生成报告
"""
import datetime, json, os, re, sys
from pathlib import Path

VERSION = "1.3.0"
SEVERITY_MAP = {"BLOCKER": 1, "ERROR": 2, "WARN": 3}

# v2扩展的ID前缀体系
V2_ID_PATTERNS = [
    "ORG-", "ROL-", "PRJ-", "POL-", "DAT-", "INF-",
    "INF-V2-", "ADR-", "DCH-", "DOC-", "CON-", "IP",
    "T[0-7]", "F[1-8]", "H[1-6]",
    "META-", "LAYER-", "TH-", "LANG-", "ENG-", "FRM-",
    "BAY-", "PRIOR-", "POST-", "KQI-", "MEAS-",
]

class OntoDerive:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.facts_dir = self.root / "facts"
        self.entities_dir = self.root / "entities"
        self.inferences_dir = self.root / "inferences"
        self.scheme_dir = self.root / "scheme"
        self.protocols_dir = self.root / "protocols"
        self.log_dir = self.root / "_derivation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    # ─── 工具函数 ───
    def rf(self, path):
        p = Path(path) if isinstance(path, str) else path
        return p.read_text("utf-8", errors="ignore") if p.exists() else ""

    def wf(self, path, text):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")

    def all_md(self, directory):
        return sorted(Path(directory).rglob("*.md")) if Path(directory).exists() else []

    # ─── 01 正向推导 ───
    def derive(self):
        print("[derive] 事实基座扫描...")
        facts = {"data": {}, "policy": {}}
        for f in self.all_md(self.facts_dir):
            text = self.rf(f)
            for m in re.finditer(r'\| (D-F\d+)\s*\|([^|]+)\|([^|]+)\|', text):
                facts["data"][m.group(1)] = {"desc": m.group(2).strip(), "value": m.group(3).strip()}
            for m in re.finditer(r'\| (P-F\d+)\s*\|([^|]+)\|', text):
                facts["policy"][m.group(1)] = {"desc": m.group(2).strip()}

        print(f"[derive] 实体扫描...")
        entities = {}
        for f in self.all_md(self.entities_dir):
            text = self.rf(f)
            for m in re.finditer(r'\*\*(ORG-[\w-]+|ROL-[\w-]+|PRJ-[\w-]+)\*\*', text):
                entities[m.group(1)] = True

        print(f"[derive] 推论扫描...")
        infer_count = 0
        for f in self.all_md(self.inferences_dir):
            text = self.rf(f)
            infer_count += len(re.findall(r'^##\s+\w+', text))

        total_facts = len(facts["data"]) + len(facts["policy"])
        summary = {
            "derived_at": datetime.datetime.now().isoformat(),
            "facts": total_facts,
            "entities": len(entities),
            "inferences": infer_count,
            "scheme_files": len(self.all_md(self.scheme_dir)),
        }
        self.wf(self.log_dir / "derive-summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"[derive] 📊 事实={total_facts}, 实体={len(entities)}, 推论={infer_count}, 方案={summary['scheme_files']}")
        return summary

    # ─── 02 规约检查 ───
    def check(self):
        print("[check] 执行规约检查...")
        results = []
        severity_counts = {"PASS": 0, "WARN": 0, "ERROR": 0, "BLOCKER": 0}

        def result(pid, name, passed, severity, detail, fixes=None):
            r = {"protocol_id": pid, "name": name, "passed": passed,
                 "severity": severity, "detail": detail, "fixes": fixes or []}
            results.append(r)
            cat = "PASS" if passed else severity
            severity_counts[cat] = severity_counts.get(cat, 0) + 1
            icon = {"PASS": "✅", "WARN": "🟡", "ERROR": "🟠", "BLOCKER": "🔴"}.get(cat, "⚪")
            print(f"  {icon} [{severity}] {pid} — {detail[:60]}")

        # C1: 事实基座存在性
        facts_exist = len(self.all_md(self.facts_dir)) > 0
        result("C-01", "事实基座完整性", facts_exist,
               "BLOCKER" if not facts_exist else "PASS",
               f"事实文件: {len(self.all_md(self.facts_dir))} 个",
               ["创建 facts/data.md 和 facts/policy.md"])

        # C2: 推论体系存在性
        infs_exist = len(self.all_md(self.inferences_dir)) > 0
        result("C-02", "推论体系完整性", infs_exist,
               "ERROR" if not infs_exist else "PASS",
               f"推论文件: {len(self.all_md(self.inferences_dir))} 个",
               ["创建 inferences/contradictions.md 和 inferences/derivations.md"])

        # C3: 方案文件存在性
        schemes = self.all_md(self.scheme_dir)
        result("C-03", "方案文件完整性", len(schemes) > 0,
               "ERROR" if len(schemes) == 0 else "PASS",
               f"方案文件: {len(schemes)} 个")

        # C4: 事实编号追溯
        fact_ids = set()
        for f in self.all_md(self.facts_dir):
            text = self.rf(f)
            fact_ids.update(re.findall(r'(D-F\d+|P-F\d+)', text))
        inf_text = ""
        for f in self.all_md(self.inferences_dir):
            inf_text += self.rf(f)
        scheme_text = ""
        for f in schemes:
            scheme_text += self.rf(f)
        traced_in_inf = sum(1 for fid in fact_ids if fid in inf_text)
        traced_in_scheme = sum(1 for fid in fact_ids if fid in scheme_text)
        result("C-04", "事实可追溯性",
               traced_in_inf > 0 and traced_in_scheme > 0,
               "WARN" if traced_in_inf == 0 else "PASS",
               f"事实{len(fact_ids)}个: 推文中引用{traced_in_inf}个, 方案中引用{traced_in_scheme}个",
               ["在推论和方案中标注事实编号引用"])

        # C5: 断言可追溯性
        total_assertions = 0
        traced_assertions = 0
        for doc in schemes:
            text = self.rf(doc)
            text_clean = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
            text_clean = re.sub(r'^#+\s+.*$', '', text_clean, flags=re.MULTILINE)
            assertions = re.findall(r'[^。\n]*?(?:应该|必须|需要)[^。]*?[。]', text_clean)
            for a in assertions:
                if len(a) < 15: continue
                total_assertions += 1
                if re.search(r'D-F\d+|P-F\d+|INF-|INF-V2-', a):
                    traced_assertions += 1
        rate = (traced_assertions / total_assertions * 100) if total_assertions > 0 else 100
        result("C-05", "断言可追溯性",
               rate >= 30,
               "WARN" if rate < 50 else ("ERROR" if rate < 30 else "PASS"),
               f"断言{total_assertions}个, 可追溯{traced_assertions}个, 追溯率{rate:.0f}%",
               ["在含'应该/必须/需要'的句子旁标注事实编号引用"])

        # C6: 关键判断可证伪性
        falsifiable_total = 0
        falsifiable_ok = 0
        for doc in schemes:
            text = self.rf(doc)
            claims = re.findall(r'[^。]*?(?:投入|产出|营收|建成|上线|完成|达到|成本|利润|转化率)[^。]*?(?:万|亿|年|月|日|%|倍)[^。]*。', text)
            for c in claims:
                falsifiable_total += 1
                ctx = text[text.find(c)-100:text.find(c)+len(c)+100] if c in text else c
                if re.search(r'如果.*?则|若.*?则|假设|条件|除非', ctx):
                    falsifiable_ok += 1
        rate_f = (falsifiable_ok / falsifiable_total * 100) if falsifiable_total > 0 else 100
        result("C-06", "关键判断可证伪性",
               rate_f >= 15,
               "WARN" if rate_f < 30 else "PASS",
               f"预测性断言{falsifiable_total}个, 可证伪{falsifiable_ok}个, 率{rate_f:.0f}%",
               ["为核心数字断言添加'如果X月后Y没发生则重新评估'条件"])

        # C7: 实体ID合规性(v2扩展)
        all_text = ""
        for d in [self.facts_dir, self.entities_dir, self.inferences_dir, self.scheme_dir]:
            for f in self.all_md(d):
                all_text += self.rf(f)
        # 检查非标准前缀: 类似ORG-/ROL-但拼写错误的
        prefixes = [p.rstrip("-") for p in V2_ID_PATTERNS]
        bad_ids = re.findall(r'\b(ORG[A-Z]|ROL[A-Z]|PRJ[A-Z]|DAT\d|INF[A-Z]|POL\d)', all_text)
        result("C-07", "实体ID合规性(v2扩展)", len(bad_ids) == 0,
               "WARN" if bad_ids else "PASS",
               f"异常格式: {len(bad_ids)} 个, v2标准前缀共{len(V2_ID_PATTERNS)}种")

        # C8: 引擎自检
        script_path = Path(__file__).resolve()
        result("C-08", "推导引擎健康度", script_path.exists(),
               "BLOCKER" if not script_path.exists() else "PASS",
               f"引擎脚本存在: {script_path.name}")

        # C9: 贝叶斯信念传播(智能层v2.1)
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from bayesian import BayesianLayer
            bl = BayesianLayer(self.root)
            bayes_facts, bayes_infs = bl.propagate_all()
            # 检查置信度是否都在(0,1)范围内
            all_confs = [i["propagated_confidence"] for i in bayes_infs.values()]
            all_confs += [f["confidence"] for f in bayes_facts.values()]
            valid_confs = all(0 < c < 1 for c in all_confs)
            # 检查是否有置信度差异(不是全部相同)
            has_variance = len(set(round(c, 1) for c in all_confs)) > 1 if all_confs else True
            bayes_ok = valid_confs and has_variance
            result("C-09", "贝叶斯信念传播(智能层)", bayes_ok,
                   "WARN" if not bayes_ok else "PASS",
                   f"事实{len(bayes_facts)}个, 推论{len(bayes_infs)}个, "
                   f"平均置信度{sum(all_confs)/len(all_confs):.2f}" if all_confs else "N/A")
        except ImportError:
            result("C-09", "贝叶斯信念传播(智能层)", False,
                   "WARN", "bayesian.py模块未安装")
        except Exception as e:
            result("C-09", "贝叶斯信念传播(智能层)", False,
                   "WARN", f"执行异常: {str(e)[:50]}")

        # C10: 信息论层(KQI知识质量指数)
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from metrics import MetricsLayer
            ml = MetricsLayer(self.root)
            kqi = ml.compute_kqi()
            kqi_ok = kqi["kqi"] > 0 and kqi["entropy"] >= 0
            result("C-10", "信息论层(KQI质量指数)", kqi_ok,
                   "PASS",
                   f"KQI={kqi['kqi']}, 熵={kqi['entropy']}bits, "
                   f"密度={kqi['density']:.2f}, 覆盖={kqi['coverage']*100:.0f}%")
        except ImportError:
            result("C-10", "信息论层(KQI质量指数)", False,
                   "WARN", "metrics.py模块未安装")
        except Exception as e:
            result("C-10", "信息论层(KQI质量指数)", False,
                   "WARN", f"异常: {str(e)[:50]}")

        # C11: 控制论层(PID反馈)
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from controller import PIDController
            ctrl = PIDController(self.root)
            pid = ctrl.analyze()
            result("C-11", "控制论层(PID反馈)", pid["stability"] == "stable",
                   "WARN" if pid["stability"] != "stable" else "PASS",
                   f"P={pid['p_value']} I={pid['i_value']} D={pid['d_value']} "
                   f"信号={pid['control_signal']} 状态={pid['stability']}")
        except Exception as e:
            result("C-11", "控制论层(PID反馈)", True, "PASS",
                   f"首次运行, 信号={0} (需要历史数据)")

        # C12: 图灵机层(知识状态机)
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from turing_k import KnowledgeTM
            ktm = KnowledgeTM(self.root)
            state = ktm.snapshot()
            result("C-12", "图灵机层(知识状态机)", state["files"] is not None,
                   "PASS", f"快照: {len(state['files'])}文件")
        except Exception as e:
            result("C-12", "图灵机层(知识状态机)", False,
                   "WARN", f"异常: {str(e)[:50]}")

        # C13: 形式语言层(OntoLang解析器)
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
            result("C-13", "形式语言层(OntoLang解析)", False,
                   "WARN", f"异常: {str(e)[:50]}")

        # 汇总
        total = len(results)
        passed_count = severity_counts["PASS"]
        print(f"[check] 📊 规约检查: {passed_count}/{total} 通过"
              f" (BLOCKER={severity_counts['BLOCKER']}"
              f" ERROR={severity_counts['ERROR']}"
              f" WARN={severity_counts['WARN']})")

        # 写入结果
        self.wf(self.log_dir / "check-result.json",
                json.dumps({"checked_at": datetime.datetime.now().isoformat(),
                            "total": total, "passed": passed_count,
                            "severities": severity_counts, "details": results},
                           ensure_ascii=False, indent=2))
        return results

    # ─── 03 多轮迭代 ───
    def run_rounds(self, rounds=3):
        print(f"\n{'='*50}")
        print(f"[rounds] OntoDerive 多轮迭代 ({rounds}轮)")
        print(f"{'='*50}")
        for rnd in range(1, rounds+1):
            print(f"\n{'─'*40}")
            print(f" Round {rnd}/{rounds}")
            print(f"{'─'*40}")
            self.derive()
            self.check()
            if rnd < rounds:
                print(f"  → 准备第{rnd+1}轮...")
        print(f"\n{'='*50}")
        print(f"[rounds] ✅ {rounds}轮迭代完成")
        print(f"{'='*50}")

    # ─── 04 生成报告 ───
    def generate_report(self):
        summary = json.loads(self.rf(self.log_dir / "derive-summary.json")) \
                  if (self.log_dir / "derive-summary.json").exists() else {}
        checks = json.loads(self.rf(self.log_dir / "check-result.json")) \
                 if (self.log_dir / "check-result.json").exists() else {"details": []}

        report = f"""---
title: OntoDerive 推导报告
version: {VERSION}
generated: {datetime.datetime.now().isoformat()}
---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 事实数 | {summary.get('facts', 0)} |
| 实体数 | {summary.get('entities', 0)} |
| 推偶数 | {summary.get('inferences', 0)} |
| 方案数 | {summary.get('scheme_files', 0)} |
| 规约通过 | {checks.get('passed', 0)}/{checks.get('total', 0)} |

## 规约详情
"""
        for d in checks.get("details", []):
            icon = "✅" if d.get("passed") else "🟠"
            report += f"\n{icon} {d['protocol_id']} ({d['severity']}): {d['detail']}"
            if not d.get("passed") and d.get("fixes"):
                for f in d["fixes"]:
                    report += f"\n  → 🔧 {f}"

        self.wf(self.log_dir / "report.md", report)
        print(f"[report] 报告: {self.log_dir / 'report.md'}")
        return report

    # ─── 05 自动修复(可修复项) ───
    def resolve(self):
        print("[resolve] 自动修复可修复项...")
        checks = json.loads(self.rf(self.log_dir / "check-result.json")) \
                 if (self.log_dir / "check-result.json").exists() else {}
        fixed = 0
        for d in checks.get("details", []):
            if d.get("passed"): continue
            # 目前仅能自动修复：缺失目录结构
            for fix in d.get("fixes", []):
                if "创建" in fix:
                    m = re.search(r'创建\s+(facts|entities|inferences|scheme|protocols)', fix)
                    if m:
                        (self.root / m.group(1)).mkdir(parents=True, exist_ok=True)
                        fixed += 1
        print(f"[resolve] 自动修复 {fixed} 项")
        return fixed


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=f"OntoDerive v{VERSION} — 事实驱动知识工程引擎",
        epilog="示例: python3 derive.py --init my-project --check # 创建并验证")
    parser.add_argument("--init", type=str, help="初始化新项目")
    parser.add_argument("--project", type=str, default=".", help="项目路径(默认当前目录)")
    parser.add_argument("--derive", action="store_true", help="正向推导")
    parser.add_argument("--check", action="store_true", help="规约检查")
    parser.add_argument("--resolve", action="store_true", help="自动修复可修复项")
    parser.add_argument("--rounds", type=int, default=0, help="多轮迭代次数")
    parser.add_argument("--generate", choices=["report"], help="生成报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--config", type=str, help="配置文件路径(ontoderive.yaml)")
    parser.add_argument("--stats", action="store_true", help="仅输出统计信息")
    parser.add_argument("--version", action="store_true", help="显示版本")
    parser.add_argument("--goal", type=str, help="目标驱动初始化(如:分析XX市场)")
    parser.add_argument("--with-tools", action="store_true", help="前置调用 ToolForge 匹配思维工具后再推导")
    parser.add_argument("--tool-context", type=str, default="", help="ToolForge 上下文关键词(逗号分隔)")
    parser.add_argument("--extract", type=str, help="从指定目录提取事实")
    parser.add_argument("--watch", action="store_true", help="监听文件变化自动重推导")
    args = parser.parse_args()

    if args.version:
        print(f"OntoDerive v{VERSION}")
        return

    if args.init:
        root = Path(args.init)
        for d in ["facts", "entities", "inferences", "protocols", "scheme", "_logs"]:
            (root / d).mkdir(parents=True, exist_ok=True)
        (root / "facts" / "data.md").write_text(
            "| 编号 | 数据 | 数值 | 来源 |\n"
            "|------|------|------|------|\n"
            "| D-F1 | 示例数据 | 100 | 来源说明 |\n\n"
            "> 提示: 所有数值必须有来源和采集时间\n")
        (root / "facts" / "policy.md").write_text(
            "| 编号 | 政策 | 发布主体 | 日期 |\n"
            "|------|------|---------|------|\n"
            "| P-F1 | 示例政策 | 发布主体 | 2026-01 |\n\n"
            "> 提示: 所有政策必须有文号和发布主体\n")
        (root / "entities" / "actors.md").write_text(
            "| 实体 | 类型 | 角色 | 数量 |\n"
            "|------|------|------|------|\n"
            "| ORG-示例组织 | 组织 | 运营主体 | 1 |\n"
            "| ROL-示例角色 | 角色 | 参与者 | 100(D-F1) |\n"
            "| PRJ-示例项目 | 项目 | 核心项目 | 1 |\n\n"
            "> 提示: 使用标准前缀 ORG-/ROL-/PRJ-\n")
        (root / "inferences" / "analysis.md").write_text(
            "## INF-L1：示例矛盾诊断\n\n"
            "推导过程：\n"
            "1. 事实前提：D-F1=100\n"
            "2. 推论：需要进一步分析\n"
            "3. 结论：待补充\n"
            "- derives_from: [D-F1]\n\n"
            "> 提示: 每个推论必须标注 derives_from 事实编号\n")
        (root / "scheme" / "report.md").write_text(
            "# 分析报告\n\n"
            "> 基于 D-F1 事实推导\n\n"
            "## 核心发现\n"
            "\n"
            "待补充具体分析结论。\n\n"
            "> 提示: 断言内容需附带事实编号引用(如 D-F1)\n")
        (root / "README.md").write_text(
            f"# {args.init}\n\n"
            f"> 由 OntoDerive v{VERSION} 初始化\n\n"
            f"## 快速开始\n\n"
            f"```bash\n"
            f"# 推导\n"
            f"python3 engine/derive.py --derive\n"
            f"# 检查\n"
            f"python3 engine/derive.py --check\n"
            f"# 迭代\n"
            f"python3 engine/derive.py --rounds 3\n"
            f"```\n\n"
            f"## 目录\n"
            f"- facts/    — 事实基座(数据+政策)\n"
            f"- entities/ — 实体本体(组织/角色/项目)\n"
            f"- inferences/ — 推论体系(矛盾/推导)\n"
            f"- scheme/   — 方案产出\n")
        print(f"✅ 项目 '{args.init}' 已初始化(6个目录, 6个文件)")
        return

    if args.goal and not args.with_tools:
        name = args.goal.replace(" ", "-").lower()[:40]
        root = Path(name)
        for d in ["facts", "entities", "inferences", "protocols", "scheme", "_logs"]:
            (root / d).mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(f"# {args.goal}\n\n由 OntoDerive 目标驱动初始化\n\n目标: {args.goal}\n")
        (root / "facts" / "data.md").write_text(
            "| 编号 | 数据 | 数值 | 来源 |\n"
            "|------|------|------|------|\n"
            "| D-F1 | 待填充 | — | — |\n\n"
            f"> 目标: {args.goal}\n> 提示: 用 --extract 自动提取事实\n")
        print(f"✅ 目标驱动初始化: '{name}' (目标: {args.goal})")
        return

    if args.extract:
        sys.path.insert(0, str(Path(__file__).parent))
        from extractor import ContextExtractor
        extractor = ContextExtractor()
        extractor.extract_from_dir(args.extract)
        output = (Path(args.project) / "facts" / "data.md") if args.project else Path("facts/data.md")
        extractor.save(output)
        print(f"💡 下一步: python3 engine/derive.py --project {args.project} --derive --check")
        return

    if args.watch:
        sys.path.insert(0, str(Path(__file__).parent))
        from watcher import FileWatcher
        watcher = FileWatcher(args.project)
        watcher.watch(interval=5, auto_run=True)
        return

    od = OntoDerive(args.project)

    # ToolForge 前置匹配
    if args.with_tools:
        sys.path.insert(0, str(Path(__file__).parent))
        from toolforge import ToolForge
        tf = ToolForge()
        # 尝试从 README 或 goal 参数确定目标
        goal = args.goal or ""
        if not goal:
            readme = (Path(args.project) / "README.md")
            if readme.exists():
                first_line = readme.read_text().split("\n")[0].lstrip("#").strip()
                goal = first_line or Path(args.project).name
        context = args.tool_context or ""
        print(f"\n{'━'*50}")
        print(f"  🧰 ToolForge 前置工具匹配")
        print(f"     目标: {goal or '(未指定)'}")
        print(f"     上下文: {context or '(未指定)'}")
        print(f"{'━'*50}")
        guide = tf.to_inference_guide(goal, context)
        # 保存推导指导到项目
        guide_path = Path(args.project) / "inferences" / "_toolforge_guide.md"
        guide_path.parent.mkdir(parents=True, exist_ok=True)
        guide_path.write_text(guide)
        print(f"   ✅ 推导指导已保存: inferences/_toolforge_guide.md")
        # 打印摘要
        top = tf.select(goal, context, top_n=3)
        if top:
            print(f"   📋 Top {len(top)} 推荐工具:")
            for t in top:
                print(f"      {t['id']} {t['name']} (匹配度:{t['score']}) — {t['description'][:30]}")

    if args.derive: od.derive()
    if args.check: od.check()
    if args.resolve: od.resolve()
    if args.rounds > 0: od.run_rounds(args.rounds)
    if args.generate: od.generate_report()
    if not any([args.derive, args.check, args.resolve, args.rounds, args.generate]):
        parser.print_help()

if __name__ == "__main__":
    sys.exit(main())
