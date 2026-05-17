"""
OntoDerive 贝叶斯层 — 信念传播与置信度管理
============================================
将置信度从离散标签(high/medium/low)升级为连续概率 P(e) ∈ [0,1]。
当事实基座更新时,自动沿 derives_from 链传播置信度变化。

用法:
    from engine.bayesian import BayesianLayer
    bl = BayesianLayer(project_root)
    bl.propagate_all()       # 全量信念传播
    bl.confidence_report()   # 输出置信度报告
"""
import datetime, json, re
from pathlib import Path

# 置信度标签 → 连续概率映射
CONFIDENCE_MAP = {
    "fact": 0.95,
    "high": 0.92,
    "inference": 0.85,
    "medium": 0.70,
    "hypothesis": 0.50,
    "low": 0.30,
    "estimated": 0.25,
    "assumption": 0.10,
}

# 传播衰减因子
DIRECT_FACTOR = 0.90      # 直接推导: INF derives_from D-Fx
INDIRECT_FACTOR = 0.80    # 间接推导: INF2 derives_from INF1

class BayesianLayer:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.facts_dir = self.root / "facts"
        self.inferences_dir = self.root / "inferences"
        self.log_dir = self.root / "_derivation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def rf(self, path):
        p = Path(path) if isinstance(path, str) else path
        return p.read_text("utf-8", errors="ignore") if p.exists() else ""

    def wf(self, path, text):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")

    def all_md(self, directory):
        return sorted(Path(directory).rglob("*.md")) if Path(directory).exists() else []

    def scan_facts(self):
        """扫描事实基座,提取所有事实及其置信度"""
        facts = {}
        for f in self.all_md(self.facts_dir):
            text = self.rf(f)
            for m in re.finditer(r'\| (D-F\d+|P-F\d+)\s*\|([^|]+)\|([^|]+)\|', text):
                fid = m.group(1)
                desc = m.group(2).strip()
                value = m.group(3).strip()
                # 事实默认置信度为0.95
                facts[fid] = {"desc": desc, "value": value, "confidence": 0.95, "type": "fact"}
        return facts

    def scan_inferences(self):
        """扫描推论,提取所有推论及其derives_from链和原始置信度标签"""
        inferences = {}
        for f in self.all_md(self.inferences_dir):
            text = self.rf(f)
            # 提取推论块(以##开头的节)
            blocks = re.split(r'^##\s+', text, flags=re.MULTILINE)
            for block in blocks[1:]:
                lines = block.strip().split("\n")
                title = lines[0].strip() if lines else "unknown"
                full_text = block

                # 提取 derives_from
                df = re.findall(r'(D-F\d+|P-F\d+)', full_text)
                # 提取原始置信度标签
                conf_match = re.search(r'confidence:\s*(\w+)', full_text)
                raw_conf = conf_match.group(1) if conf_match else "inference"
                base_conf = CONFIDENCE_MAP.get(raw_conf, 0.85)

                inferences[title] = {
                    "derives_from": list(set(df)),
                    "raw_confidence": raw_conf,
                    "base_confidence": base_conf,
                    "propagated_confidence": None,
                    "text": full_text[:200],
                }
        return inferences

    def propagate(self, facts, inferences):
        """执行信念传播:沿derives_from链传播置信度"""
        # 第一轮: 直接从事实推导的推论
        for name, inf in inferences.items():
            premises = [f for f in inf["derives_from"] if f in facts]
            if premises:
                avg_premise_conf = sum(facts[p]["confidence"] for p in premises) / len(premises)
                inf["propagated_confidence"] = round(avg_premise_conf * DIRECT_FACTOR, 4)
            else:
                # 无直接事实前提,用基础置信度
                inf["propagated_confidence"] = inf["base_confidence"]

        # 第二轮: INF推导INF(间接传播)
        changed = True
        max_iter = 10
        while changed and max_iter > 0:
            changed = False
            max_iter -= 1
            for name, inf in inferences.items():
                # 检查derives_from中是否有其他INF
                indirect_premises = [n for n in inferences if n in inf["derives_from"]]
                if indirect_premises:
                    avg_indirect = sum(inferences[n]["propagated_confidence"] for n in indirect_premises) / len(indirect_premises)
                    new_conf = round(avg_indirect * INDIRECT_FACTOR, 4)
                    if new_conf < inf["propagated_confidence"]:
                        inf["propagated_confidence"] = new_conf
                        changed = True

        # 归一化: 确保置信度在[0,1]范围内
        for inf in inferences.values():
            inf["propagated_confidence"] = max(0.01, min(0.99, inf["propagated_confidence"]))

        return inferences

    def propagate_all(self):
        """全量信念传播"""
        facts = self.scan_facts()
        inferences = self.scan_inferences()
        inferences = self.propagate(facts, inferences)
        return facts, inferences

    def confidence_report(self):
        """生成置信度报告"""
        facts, inferences = self.propagate_all()

        report = f"""---
title: 贝叶斯信念传播报告
generated: {datetime.datetime.now().isoformat()}
---

## 事实基座置信度

| 编号 | 简介 | 置信度 |
|------|------|--------|
"""
        for fid, info in sorted(facts.items()):
            report += f"| {fid} | {info['desc'][:30]} | {info['confidence']:.2f} |\n"

        report += "\n## 推论置信度(传播后)\n\n"
        report += "| 推论 | 原始标签 | 传播后置信度 | derives_from |\n"
        report += "|------|---------|-------------|-------------|\n"
        for name, info in sorted(inferences.items()):
            report += f"| {name[:40]} | {info['raw_confidence']} | {info['propagated_confidence']:.2f} | {', '.join(info['derives_from'][:5])} |\n"

        report += "\n## 熵\n\n"
        # 简单熵计算: -Σ P*log(P)
        import math
        all_confs = [i["propagated_confidence"] for i in inferences.values()] + [f["confidence"] for f in facts.values()]
        entropy = 0
        for c in all_confs:
            if c > 0 and c < 1:
                entropy += -c * math.log2(c) - (1-c) * math.log2(1-c)
        report += f"知识库总熵: {entropy:.4f} bits\n"
        report += f"平均置信度: {sum(all_confs)/len(all_confs):.4f}\n"
        report += f"推论数: {len(inferences)}\n"
        report += f"事实数: {len(facts)}\n"

        report_path = self.log_dir / "bayesian-report.md"
        self.wf(report_path, report)
        print(f"[bayesian] ✅ 信念传播报告: {report_path}")
        return report
