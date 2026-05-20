"""
OntoDerive 生态适配器 — Agora MCP路由
======================================
将MCP调用映射到OntoDerive Pipeline/工具
"""
from pathlib import Path


def _import_derive():
    try:
        from .derive import OntoDerive
    except ImportError:
        from derive import OntoDerive  # noqa
    return OntoDerive


def _import_toolforge():
    try:
        from ..toolforge.matcher import ToolForge
    except ImportError:
        from toolforge.matcher import ToolForge  # noqa
    return ToolForge


class AgoraAdapter:
    """Agora MCP路由适配器 — 按工具名前缀路由到OntoDerive MCP"""

    TOOL_PREFIX = "ontoderive_"
    TOOLFORGE_PREFIX = "toolforge_"

    @classmethod
    def can_handle(cls, tool_name: str) -> bool:
        return tool_name.startswith(cls.TOOL_PREFIX) or tool_name.startswith(cls.TOOLFORGE_PREFIX)

    @classmethod
    def route(cls, tool_name: str, arguments: dict, project_root: str = ".") -> dict:
        """将Agora的MCP调用转为本地OntoDerive调用"""
        root = Path(project_root)

        if tool_name.startswith(cls.TOOLFORGE_PREFIX):
            tf = _import_toolforge()()
            goal = arguments.get("goal", "")
            context = arguments.get("context", "")
            if tool_name == "toolforge_match":
                return tf.match(goal, context)
            elif tool_name == "toolforge_select":
                return {"tools": tf.select(goal, context, top_n=arguments.get("top_n", 5))}
            elif tool_name == "toolforge_guide":
                return {"guide": tf.to_inference_guide(goal, context)}

        if tool_name.startswith(cls.TOOL_PREFIX):
            od = _import_derive()(root)
            if tool_name == "ontoderive_derive":
                return od.derive()
            elif tool_name == "ontoderive_check":
                return {"results": od.check()}
            elif tool_name == "ontoderive_rounds":
                od.run_rounds(arguments.get("rounds", 3))
                return {"status": "done"}
            elif tool_name == "ontoderive_generate":
                return {"report": od.generate_report()}

        return {"error": f"Unsupported tool: {tool_name}"}
