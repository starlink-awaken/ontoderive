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

VERSION = "2.2.0"


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
            infer_count += len(re.findall(r'^##\s+\w+', rf(f)))

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
        except Exception: pass

        try:
            from logic import build_from_project
            g = build_from_project(self.root).stats()
            summary["entailment_graph"] = {"nodes": g["nodes"], "edges": g["edges"], "max_depth": g["max_depth"], "cycles": g["cycles"]}
        except Exception: pass

        save_json(self.log_dir / "derive-summary.json", summary)
        print(f"[derive] 📊 事实={summary['facts']}, 推论={summary['inferences']}")
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
