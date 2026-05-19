#!/usr/bin/env python3
"""
OntoDerive 推导引擎 v2.2
=========================
事实驱动推导引擎：事实→本体→推论→方案的全链路可追溯推导。
支持多轮迭代、双向规约校验、断言追溯检测、实体完整性检查。

用法:
    python3 derive.py --init my-project     # 初始化
    python3 derive.py --derive              # 正向推导
    python3 derive.py --check               # 规约检查
    python3 derive.py --rounds 5            # 多轮迭代
    python3 derive.py --generate report     # 生成报告
"""
import datetime, re, sys
from pathlib import Path

try:
    from .utils import rf, wf, all_md, load_json, save_json
except ImportError:
    from utils import rf, wf, all_md, load_json, save_json  # noqa

VERSION = "3.0.0"

try:
    from .protocols import DeriveInterface
except ImportError:
    from protocols import DeriveInterface  # noqa


class OntoDerive(DeriveInterface):
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.facts_dir = self.root / "facts"
        self.entities_dir = self.root / "entities"
        self.inferences_dir = self.root / "inferences"
        self.scheme_dir = self.root / "scheme"
        self.protocols_dir = self.root / "protocols"
        self.log_dir = self.root / "_derivation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def derive(self):
        print("[derive] 事实基座扫描...")
        facts = {"data": {}, "policy": {}}
        for f in all_md(self.facts_dir):
            text = rf(f)
            for m in re.finditer(r'\| (D-F\d+)\s*\|([^|]+)\|([^|]+)\|', text):
                facts["data"][m.group(1)] = {"desc": m.group(2).strip(), "value": m.group(3).strip()}
            for m in re.finditer(r'\| (P-F\d+)\s*\|([^|]+)\|', text):
                facts["policy"][m.group(1)] = {"desc": m.group(2).strip()}

        entities = {}
        for f in all_md(self.entities_dir):
            for m in re.finditer(r'\*\*(ORG-[\w-]+|ROL-[\w-]+|PRJ-[\w-]+)\*\*', rf(f)):
                entities[m.group(1)] = True

        infer_count = 0
        for f in all_md(self.inferences_dir):
            infer_count += len(re.findall(r'^##\s+INF-', rf(f), re.MULTILINE))

        summary = {"derived_at": datetime.datetime.now().isoformat(),
                   "facts": len(facts["data"]) + len(facts["policy"]),
                   "entities": len(entities), "inferences": infer_count,
                   "scheme_files": len(all_md(self.scheme_dir))}

        # v2.1: 集成贝叶斯置信度分布+逻辑链深度
        try:
            from bayesian import BayesianLayer
            bl = BayesianLayer(self.root)
            _, bayes_infs = bl.propagate_all()
            confs = [i.get("propagated_confidence", i.get("base_confidence", 0.85)) for i in bayes_infs.values()]
            if confs:
                summary["confidence_distribution"] = {"mean": round(sum(confs)/len(confs),4), "min": round(min(confs),4), "max": round(max(confs),4), "count": len(confs)}
        except Exception as e:
            import sys; print(f"[derive] Bayesian skip: {e}", file=sys.stderr)

        try:
            from logic import build_from_project
            g = build_from_project(self.root).stats()
            summary["entailment_graph"] = {"nodes": g["nodes"], "edges": g["edges"], "max_depth": g["max_depth"], "cycles": g["cycles"]}
        except Exception as e:
            import sys; print(f"[derive] Logic skip: {e}", file=sys.stderr)

        # v2.3: 内容推导 — 规则引擎 + DAG分析
        derivation_hints = []
        for f in all_md(self.inferences_dir):
            text = rf(f)
            if "derives_from" not in text:
                derivation_hints.append(f"{f.name}: 缺少 derives_from 声明")
            if "理论支撑" not in text and "理论" not in text:
                derivation_hints.append(f"{f.name}: 建议添加理论支撑")
        for f in all_md(self.scheme_dir):
            text = rf(f)
            if len(re.findall(r'D-F\d+|P-F\d+', text)) == 0:
                derivation_hints.append(f"{f.name}: 未引用任何事实编号")

        # DAG分析：弱推论、矛盾检测
        try:
            from logic import build_from_project
            g = build_from_project(self.root)
            st = g.stats()
            if st["contradictions"]:
                for c in st["contradictions"]:
                    derivation_hints.append(
                        f"⚠️ 矛盾: {c['inference_a']} vs {c['inference_b']} "
                        f"(共享事实{c['shared_facts']}, 对立词{c['opposing_terms']})")
            if st["max_depth"] < 2 and st["inferences"] >= 3:
                derivation_hints.append(f"推导链深度仅{st['max_depth']}，推论间缺少递进关系")
            if st["has_cycles"]:
                derivation_hints.append(f"检测到{st['cycles']}个循环引用，请检查 derives_from 链")
        except Exception:
            pass

        # v2.4: LLM增强推导提示（降级：无LLM时跳过）
        try:
            from llm import get_enhancer
            enhancer = get_enhancer()
            if enhancer.available:
                infs_text = "\n".join(rf(f) for f in all_md(self.inferences_dir))
                hints_before = len(derivation_hints)
                derivation_hints = enhancer.enhance_derivation_hints(
                    f"事实数={summary['facts']}, 推论数={summary['inferences']}",
                    infs_text, derivation_hints)
                if len(derivation_hints) > hints_before:
                    print(f"[derive] 🤖 LLM增强: +{len(derivation_hints)-hints_before}条洞察 ({enhancer.model})")
                else:
                    print(f"[derive] 🤖 LLM就绪 ({enhancer.model}), 规则引擎已覆盖当前场景")
        except Exception:
            pass

        if derivation_hints:
            summary["derivation_hints"] = derivation_hints[:15]

        save_json(self.log_dir / "derive-summary.json", summary)
        print(f"[derive] 📊 事实={summary['facts']}, 推论={summary['inferences']}, 推导提示={len(derivation_hints)}")
        return summary

    def check(self):
        print("[check] 执行规约检查...")
        try:
            from .check import run_check
        except ImportError:
            from check import run_check  # noqa
        return run_check(self.root, self.facts_dir, self.entities_dir,
                         self.inferences_dir, self.scheme_dir, self.log_dir)[0]

    def run_rounds(self, rounds=3):
        for rnd in range(1, rounds+1):
            print(f"\n Round {rnd}/{rounds}")
            self.derive()
            self.check()
        print(f"[rounds] ✅ {rounds}轮迭代完成")

    def generate_report(self):
        summary = load_json(self.log_dir / "derive-summary.json") or {}
        checks = load_json(self.log_dir / "check-result.json") or {"details": []}
        report = f"""---
title: OntoDerive 推导报告
version: {VERSION}
generated: {datetime.datetime.now().isoformat()}
---

## 执行摘要
| 指标 | 数值 |
|------|------|
| 事实数 | {summary.get('facts', 0)} |
| 推偶数 | {summary.get('inferences', 0)} |
| 规约通过 | {checks.get('passed', 0)}/{checks.get('total', 0)} |
"""
        for d in checks.get("details", []):
            report += f"\n{'✅' if d.get('passed') else '🟠'} {d['protocol_id']}: {d['detail']}"
        wf(self.log_dir / "report.md", report)
        print(f"[report] 报告: {self.log_dir / 'report.md'}")
        return report

    def resolve(self):
        checks = load_json(self.log_dir / "check-result.json") or {}
        fixed = 0
        for d in checks.get("details", []):
            if d.get("passed"): continue
            for fix in d.get("fixes", []):
                if "创建" in fix:
                    m = re.search(r'创建\s+(facts|entities|inferences|scheme|protocols)', fix)
                    if m:
                        (self.root / m.group(1)).mkdir(parents=True, exist_ok=True)
                        fixed += 1
        print(f"[resolve] 修复 {fixed} 项")
        return fixed


# CLI入口 (v2.2: 委托给cli.py)
def main():
    try: from .cli import main as _main
    except ImportError: from cli import main as _main  # noqa
    _main()

if __name__ == "__main__":
    import sys; sys.exit(main())
