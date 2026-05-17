"""
OntoDerive 控制论层 — PID反馈控制与自适应阈值
================================================
P(比例): 当前违规数 → 立即修复
I(积分): 历史违规累积 → 系统性问题检测
D(微分): 违规变化率 → 预测性告警

用法:
    from engine.controller import PIDController
    ctrl = PIDController(project_root)
    ctrl.analyze()    # 执行PID分析
    ctrl.report()     # 生成控制报告
"""
import datetime, json, math
from pathlib import Path

class PIDController:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.log_dir = self.root / "_derivation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.history = self._load_history()

    def _load_history(self):
        """加载历史检查记录作为积分项输入"""
        history = []
        for f in sorted(self.log_dir.glob("check-result.json")):
            try:
                data = json.loads(f.read_text())
                history.append(data)
            except: pass
        return history

    def analyze(self):
        """执行PID分析"""
        # P: 比例项 — 当前违规数
        current = self._get_current_violations()
        p_value = current.get("total_violations", 0)

        # I: 积分项 — 历史违规累积
        i_value = self._integral_term()

        # D: 微分项 — 违规变化率
        d_value = self._derivative_term()

        # 控制信号 = P + I + D
        control_signal = round(p_value + i_value + d_value, 2)

        # 自适应阈值
        recommended_thresholds = self._adaptive_thresholds()

        return {
            "p_value": p_value,
            "i_value": i_value,
            "d_value": d_value,
            "control_signal": control_signal,
            "stability": "stable" if abs(d_value) < 0.3 else "unstable",
            "recommended_thresholds": recommended_thresholds,
            "history_count": len(self.history),
        }

    def _get_current_violations(self):
        """获取当前检查结果"""
        latest = self.history[-1] if self.history else {}
        sevs = latest.get("severities", {})
        total = sevs.get("WARN", 0) + sevs.get("ERROR", 0) + sevs.get("BLOCKER", 0)
        return {"total_violations": total, "severities": sevs}

    def _integral_term(self):
        """积分项: 历史违规趋势"""
        if len(self.history) < 2:
            return 0.0
        total = 0
        for h in self.history:
            sevs = h.get("severities", {})
            total += sevs.get("WARN", 0) + sevs.get("ERROR", 0) + sevs.get("BLOCKER", 0)
        return round(total / len(self.history), 2)

    def _derivative_term(self):
        """微分项: 违规数变化率"""
        if len(self.history) < 2:
            return 0.0
        def get_total(h):
            sevs = h.get("severities", {})
            return sevs.get("WARN", 0) + sevs.get("ERROR", 0) + sevs.get("BLOCKER", 0)
        recent = get_total(self.history[-1])
        prev = get_total(self.history[-2])
        return round(recent - prev, 2)

    def _adaptive_thresholds(self):
        """自适应阈值推荐"""
        return {
            "assertion_traceability": ">=30%" if len(self.history) < 3 else ">=50%",
            "falsifiability": ">=15%" if len(self.history) < 3 else ">=30%",
        }

    def report(self):
        """生成控制论报告"""
        pid = self.analyze()
        report = f"""---
title: 控制论PID分析报告
generated: {datetime.datetime.now().isoformat()}
---

## PID控制信号

| 分量 | 数值 | 含义 |
|------|------|------|
| P(比例) | {pid['p_value']} | 当前违规数 |
| I(积分) | {pid['i_value']} | 历史平均违规 |
| D(微分) | {pid['d_value']} | 违规变化率 |
| **控制信号** | **{pid['control_signal']}** | P+I+D |
| 稳定性 | {pid['stability']} | D<0.3为稳定 |

## 自适应阈值建议

| 规约 | 当前建议 | 依据 |
|------|---------|------|
| C-05追溯率 | {pid['recommended_thresholds']['assertion_traceability']} | 基于{max(len(self.history),1)}次检查 |
| C-06可证伪 | {pid['recommended_thresholds']['falsifiability']} | 同上 |
"""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        (self.log_dir / "pid-report.md").write_text(report, encoding="utf-8")
        print(f"[controller] ✅ PID报告: {self.log_dir / 'pid-report.md'}")
        return pid
