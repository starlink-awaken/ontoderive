"""
OntoDerive 信息论层 — 知识质量指数(KQI)与熵计算
======================================================
基于香农信息论,量化知识库的不确定性、质量和信息增益。

用法:
    from engine.metrics import MetricsLayer
    ml = MetricsLayer(project_root)
    ml.full_report()           # 全量KQI报告
    ml.information_gain()      # 计算新增事实的信息增益
"""
import datetime, json, math, re
from pathlib import Path

class MetricsLayer:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.facts_dir = self.root / "facts"
        self.entities_dir = self.root / "entities"
        self.inferences_dir = self.root / "inferences"
        self.scheme_dir = self.root / "scheme"
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

    def entropy(self, probabilities):
        """计算香农熵 H = -Σ p*log2(p)"""
        h = 0
        for p in probabilities:
            if 0 < p < 1:
                h += -p * math.log2(p) - (1-p) * math.log2(1-p)
        return round(h, 4)

    def compute_kqi(self):
        """计算知识质量指数(KQI)"""
        # 1. 事实统计
        facts_text = ""
        for f in self.all_md(self.facts_dir):
            facts_text += self.rf(f)
        fact_ids = set(re.findall(r'(D-F\d+|P-F\d+)', facts_text))
        n_facts = len(fact_ids)

        # 2. 推论统计
        infs_text = ""
        for f in self.all_md(self.inferences_dir):
            infs_text += self.rf(f)
        inf_blocks = len(re.findall(r'^##\s+', infs_text, re.MULTILINE))
        n_inferences = max(0, inf_blocks - 1)  # 去掉文件标题

        # 3. 实体统计
        entities_text = ""
        for f in self.all_md(self.entities_dir):
            entities_text += self.rf(f)
        n_entities = len(set(re.findall(r'\*\*(ORG-[\w-]+|ROL-[\w-]+|PRJ-[\w-]+)\*\*', entities_text)))

        # 4. 方案统计
        scheme_text = ""
        for f in self.all_md(self.scheme_dir):
            scheme_text += self.rf(f)
        n_scheme_files = len(self.all_md(self.scheme_dir))

        # 5. 追溯率(事实在方案中的引用)
        traced = sum(1 for fid in fact_ids if fid in scheme_text)
        coverage = traced / n_facts if n_facts > 0 else 1.0

        # 6. 熵计算(使用假设置信度: 事实0.95, 推论0.85)
        fact_confs = [0.95] * n_facts
        inf_confs = [0.85] * n_inferences
        h_total = self.entropy(fact_confs + inf_confs)

        # 7. 推导密度
        density = n_inferences / n_facts if n_facts > 0 else 0

        # 8. KQI综合指数(加权平均)
        kqi = round((
            0.25 * (1 - h_total / max(n_facts + n_inferences, 1)) +  # 熵(越低越好)
            0.25 * coverage +                                         # 追溯率
            0.20 * min(density / 0.5, 1.0) +                         # 推导密度(目标0.5)
            0.15 * min(n_entities / max(n_facts, 1), 1.0) +          # 实体覆盖
            0.15 * min(n_scheme_files / 3, 1.0)                       # 方案文件(目标3个)
        ), 4)

        return {
            "kqi": kqi,
            "entropy": h_total,
            "n_facts": n_facts,
            "n_inferences": n_inferences,
            "n_entities": n_entities,
            "n_scheme_files": n_scheme_files,
            "coverage": round(coverage, 4),
            "density": round(density, 4),
        }

    def information_gain(self, before_kqi, after_kqi):
        """计算信息增益: IG = H(before) - H(after)"""
        return round(before_kqi["entropy"] - after_kqi["entropy"], 4)

    def full_report(self):
        """生成完整KQI报告"""
        kqi = self.compute_kqi()
        report = f"""---
title: 知识质量指数(KQI)报告
generated: {datetime.datetime.now().isoformat()}
---

## KQI综合指数: {kqi['kqi']}

| 维度 | 数值 | 权重 | 贡献 |
|------|------|------|------|
| 知识熵 | {kqi['entropy']} bits | 25% | 计算 |
| 追溯覆盖率 | {kqi['coverage']*100:.0f}% | 25% | 映射完整性 |
| 推导密度 | {kqi['density']:.2f} inf/fact | 20% | 深度 |
| 实体覆盖 | {kqi['n_entities']} 实体 | 15% | 广度 |
| 方案文件 | {kqi['n_scheme_files']} 文件 | 15% | 产出 |

## 明细

| 指标 | 数值 |
|------|------|
| 事实数 | {kqi['n_facts']} |
| 推偶数 | {kqi['n_inferences']} |
| 实体数 | {kqi['n_entities']} |
| 方案文件数 | {kqi['n_scheme_files']} |
| 知识熵 H(KB) | {kqi['entropy']} bits |
"""
        report_path = self.log_dir / "kqi-report.md"
        self.wf(report_path, report)
        print(f"[metrics] ✅ KQI报告: {report_path}")
        print(f"[metrics] 📊 KQI={kqi['kqi']}, 熵={kqi['entropy']}bits, 覆盖={kqi['coverage']*100:.0f}%")
        return kqi
