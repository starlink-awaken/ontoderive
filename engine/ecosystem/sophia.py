"""
OntoDerive 生态适配器 — Sophia集成
====================================
Sophia范式推荐 → ToolForge匹配 → OntoDerive推导指导
"""
try:
    from ..toolforge.matcher import ToolForge
except ImportError:
    from toolforge.matcher import ToolForge  # noqa


def sophia_to_toolforge(paradigm_result: dict) -> dict:
    """将Sophia范式推荐结果转为ToolForge匹配输入"""
    tf = ToolForge()
    paradigm_name = paradigm_result.get("paradigm", paradigm_result.get("name", ""))
    context = paradigm_result.get("domain", paradigm_result.get("context", ""))
    dimensions = paradigm_result.get("dimensions", [])

    # 用范式名称+维度作为查询
    goal = f"{paradigm_name} {' '.join(dimensions)}"
    matches = tf.select(goal, context, top_n=5)

    guide = tf.to_inference_guide(goal, context)

    return {
        "paradigm": paradigm_name,
        "matches": [{"id": m["id"], "name": m["name"], "score": m["score"]} for m in matches],
        "guide": guide,
    }


def recommend_frameworks(goal: str, context: str = "", top_n: int = 3) -> list:
    """为Sophia提供框架推荐（实现ToolForgeInterface）"""
    tf = ToolForge()
    return tf.select(goal, context, top_n=top_n)


def get_derivation_guide(goal: str, context: str = "") -> str:
    """为Sophia生成推导指导（实现ToolForgeInterface）"""
    tf = ToolForge()
    return tf.to_inference_guide(goal, context)
