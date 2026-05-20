"""
规则加载器 — Rule Loader (LP4 自组织)
=====================================
从YAML/JSON声明文件加载推理规则，使规则可插拔而不需改源码。

格式示例 (YAML):
  id: R22
  name: trend_detection
  type: threshold_alert
  category: analytics
  description: 检测指标的显著变化趋势
  premises: ["has_numeric_value", "change > 20%"]
  conclusion_template: "{desc}从{old}变为{new}, 变化{change}%, 趋势{trend}"
  confidence: 0.75
  method: rule_loader

支持规则类型: threshold_alert | numeric_comparison | evidence_gap | shared_premise
"""
import json
from pathlib import Path
from typing import List


class RuleLoader:
    """从YAML/JSON声明文件加载推理规则"""

    def __init__(self, rules_dir: str = None):
        self.rules_dir = Path(rules_dir) if rules_dir else None
        self.rules: List[dict] = []

    def load_json(self, path: str) -> List[dict]:
        """从JSON文件加载规则"""
        data = json.loads(Path(path).read_text())
        loaded = data if isinstance(data, list) else [data]
        self.rules.extend(self._validate(loaded))
        return loaded

    def load_yaml(self, path: str) -> List[dict]:
        """从YAML文件加载规则"""
        try:
            import yaml
        except ImportError:
            # fallback: 使用内置解析器处理简单YAML结构
            return self._load_yaml_simple(path)
        data = yaml.safe_load(Path(path).read_text())
        loaded = data if isinstance(data, list) else [data]
        self.rules.extend(self._validate(loaded))
        return loaded

    def _load_yaml_simple(self, path: str) -> List[dict]:
        """简易YAML解析器 — 零依赖fallback"""
        text = Path(path).read_text()
        rules = []
        current = {}
        for line in text.split("\n"):
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("- id:") or (line.startswith("id:") and current):
                if current:
                    rules.append(dict(current))
                current = {}
            if ":" in line and not line.startswith(" "):
                key, _, val = line.partition(":")
                key, val = key.strip(), val.strip()
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("[") and val.endswith("]"):
                    val = [v.strip().strip('"') for v in val[1:-1].split(",")]
                elif val.replace(".", "").isdigit():
                    val = float(val) if "." in val else int(val)
                elif val in ("true", "false"):
                    val = val == "true"
                current[key] = val
        if current:
            rules.append(dict(current))
        self.rules.extend(self._validate(rules))
        return rules

    def _validate(self, rules: List[dict]) -> List[dict]:
        """验证规则基本结构"""
        required = {"id", "name", "type"}
        valid = []
        for r in rules:
            missing = required - set(r.keys())
            if missing:
                print(f"[RuleLoader] 规则{r.get('id','?')}缺少字段: {missing}")
            else:
                valid.append(r)
        return valid

    def get_by_type(self, rule_type: str) -> List[dict]:
        """按类型获取规则"""
        return [r for r in self.rules if r.get("type") == rule_type]

    def get_by_category(self, category: str) -> List[dict]:
        return [r for r in self.rules if r.get("category") == category]

    def to_conclusion(self, rule: dict, **kwargs) -> dict:
        """将规则模板化为结论"""
        template = rule.get("conclusion_template", rule.get("name", ""))
        try:
            text = template.format(**kwargs)
        except KeyError:
            text = template
        return {
            "type": rule.get("type", "loaded_rule"),
            "conclusion": text,
            "confidence": rule.get("confidence", 0.70),
            "derived_from": kwargs.get("derives_from", []),
            "method": "rule_loader",
            "derivation_trail": f"{rule.get('id','Y?')}: {rule.get('name','?')}",
        }
