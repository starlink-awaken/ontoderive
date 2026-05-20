"""
OntoDerive 生态适配器 — Minerva集成
====================================
Minerva研究结果 → OntoDerive facts/ 文件
"""
from pathlib import Path
try:
    from engine.foundation.utils import wf
except ImportError:
    from engine.foundation.utils import wf  # noqa


def minerva_to_facts(research_result: dict, project_root: str):
    """将Minerva研究结果转换为OntoDerive事实基座"""
    root = Path(project_root)
    facts_dir = root / "facts"
    facts_dir.mkdir(parents=True, exist_ok=True)

    items = research_result.get("facts", []) or research_result.get("findings", [])
    lines = [
        "| 编号 | 数据 | 数值 | 来源 |",
        "|------|------|------|------|",
    ]
    for i, item in enumerate(items, 1):
        desc = item.get("description", item.get("title", f"研究事实{i}"))
        value = item.get("value", item.get("data", ""))
        source = item.get("source", item.get("url", "Minerva研究"))
        lines.append(f"| D-F{i} | {desc} | {value} | {source} |")

    lines.append(f"\n> 由Minerva研究自动生成，{len(items)}条事实")
    wf(facts_dir / "data.md", "\n".join(lines))

    policies = research_result.get("policies", [])
    if policies:
        plines = [
            "| 编号 | 政策 | 发布主体 | 日期 |",
            "|------|------|---------|------|",
        ]
        for i, p in enumerate(policies, 1):
            plines.append(f"| P-F{i} | {p.get('name', '')} | {p.get('authority', '')} | {p.get('date', '')} |")
        wf(facts_dir / "policy.md", "\n".join(plines))

    return {"facts_files": len(items), "policy_files": len(policies)}


def minerva_to_entities(research_result: dict, project_root: str):
    """将Minerva的实体发现转为OntoDerive实体文件"""
    root = Path(project_root)
    entities_dir = root / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)

    entities = research_result.get("entities", []) or research_result.get("stakeholders", [])
    lines = [
        "| 实体 | 类型 | 角色 | 数量 |",
        "|------|------|------|------|",
    ]
    for e in entities:
        eid = e.get("id", e.get("name", "ENTITY"))
        etype = e.get("type", "Organization")
        role = e.get("role", "")
        count = e.get("count", "")
        lines.append(f"| {eid} | {etype} | {role} | {count} |")

    wf(entities_dir / "actors.md", "\n".join(lines))
    return {"entities": len(entities)}
