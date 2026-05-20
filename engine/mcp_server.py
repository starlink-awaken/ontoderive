#!/usr/bin/env python3
"""
OntoDerive Unified MCP Server v3
=================================
统一入口：OntoDerive推导(5工具) + ToolForge匹配(3工具) + 新增(3工具) = 11工具
协议：JSON-RPC 2.0 over stdio，可直接注册到 Agora MCP路由层。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # 项目根
sys.path.insert(0, str(Path(__file__).parent))         # engine/
from engine.core.derive import OntoDerive
from toolforge.matcher import ToolForge

tf = ToolForge()


def respond(req_id, result):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}, ensure_ascii=False)


def err(req_id, code, message):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}, ensure_ascii=False)


TOOL_DEFS = [
    {"name": "ontoderive_init", "description": "初始化新OntoDerive项目骨架", "inputSchema": {"type": "object", "properties": {"name": {"type": "string", "description": "项目名称"}}, "required": ["name"]}},
    {"name": "ontoderive_derive", "description": "正向推导：扫描facts/entities/inferences/scheme生成摘要", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_check", "description": "规约检查：执行13条规约(C-01~C-13)含贝叶斯/KQI/PID", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_rounds", "description": "多轮迭代：derive→check循环至收敛", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}, "rounds": {"type": "number", "description": "迭代轮数", "default": 3}}}},
    {"name": "ontoderive_generate", "description": "生成推导报告(markdown)", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_analyze", "description": "全量分析：Pipeline全流程(ToolForge+derive+check)，含匹配推荐+置信度+KQI+收敛", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径"}, "goal": {"type": "string", "description": "分析目标"}, "context": {"type": "string", "description": "上下文关键词"}}}},
    {"name": "ontoderive_config", "description": "获取当前配置项(匹配模式/阈值等)", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_delta", "description": "对比最近两次推导的状态差异", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "toolforge_match", "description": "按目标匹配思维工具并按类别分组", "inputSchema": {"type": "object", "properties": {"goal": {"type": "string", "description": "目标描述"}, "context": {"type": "string", "description": "上下文"}, "mode": {"type": "string", "description": "匹配模式: tfidf|keyword|hybrid", "default": "keyword"}}, "required": ["goal"]}},
    {"name": "toolforge_select", "description": "跨类别Top-N工具选择", "inputSchema": {"type": "object", "properties": {"goal": {"type": "string", "description": "目标描述"}, "context": {"type": "string"}, "top_n": {"type": "number", "default": 5}, "mode": {"type": "string", "default": "keyword"}}, "required": ["goal"]}},
    {"name": "toolforge_guide", "description": "生成推导指导(markdown)", "inputSchema": {"type": "object", "properties": {"goal": {"type": "string", "description": "目标描述"}, "context": {"type": "string"}, "mode": {"type": "string", "default": "keyword"}}, "required": ["goal"]}},
]


def handle_request(req):
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    if method == "tools/list":
        return respond(req_id, {"tools": TOOL_DEFS})

    if method == "initialize":
        return respond(req_id, {
            "protocolVersion": "0.1.0",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ontoderive-unified-mcp", "version": "3.5.0"}
        })

    if method == "tools/call":
        tool = params.get("name", "")
        args = params.get("arguments", {})
        project = args.get("project", ".")
        name = args.get("name", "demo")

        try:
            if tool == "ontoderive_init":
                od = OntoDerive(name)
                od.derive()
                return respond(req_id, {"output": f"项目'{name}'已初始化，目录: facts/entities/inferences/scheme/"})

            elif tool in ("ontoderive_derive", "ontoderive_check", "ontoderive_generate"):
                od = OntoDerive(project)
                if tool == "ontoderive_derive":
                    result = od.derive()
                elif tool == "ontoderive_check":
                    result = od.check()
                else:
                    result = od.generate_report()
                return respond(req_id, {"output": str(result)[:1000]})

            elif tool == "ontoderive_rounds":
                od = OntoDerive(project)
                rounds = args.get("rounds", 3)
                od.run_rounds(int(rounds))
                return respond(req_id, {"output": f"{rounds}轮迭代完成，日志在 _derivation_logs/"})

            elif tool == "ontoderive_analyze":
                od = OntoDerive(project)
                goal = args.get("goal", "")
                context = args.get("context", "")
                if goal:
                    matches = tf.select(goal, context, top_n=5)
                    guide = tf.to_inference_guide(goal, context)
                else:
                    matches, guide = [], ""
                derive_r = od.derive()
                check_r = od.check()
                return respond(req_id, {
                    "derive_summary": derive_r,
                    "checks_passed": sum(1 for r in check_r if r.get("passed")),
                    "checks_total": len(check_r),
                    "toolforge_matches": [{"id": m["id"], "name": m["name"], "score": m["score"]} for m in matches],
                    "guide": guide[:500],
                })

            elif tool == "ontoderive_config":
                from engine.foundation.config import Config
                cfg = Config(project).to_dict()
                return respond(req_id, cfg)

            elif tool == "ontoderive_delta":
                from engine.theories.turing_k import KnowledgeTM
                ktm = KnowledgeTM(project)
                d = ktm.delta()
                return respond(req_id, d)

            elif tool == "toolforge_match":
                goal = args.get("goal", "")
                context = args.get("context", "")
                mode = args.get("mode", "keyword")
                result = tf.match(goal, context, mode=mode)
                return respond(req_id, result)

            elif tool == "toolforge_select":
                goal = args.get("goal", "")
                context = args.get("context", "")
                top_n = args.get("top_n", 5)
                mode = args.get("mode", "keyword")
                result = tf.select(goal, context, top_n=int(top_n), mode=mode)
                return respond(req_id, result)

            elif tool == "toolforge_guide":
                goal = args.get("goal", "")
                context = args.get("context", "")
                mode = args.get("mode", "keyword")
                guide = tf.to_inference_guide(goal, context, mode=mode)
                return respond(req_id, {"guide": guide[:2000]})

            return err(req_id, -32601, f"未知工具: {tool}")

        except Exception as e:
            return err(req_id, -32000, f"{tool}失败: {str(e)[:200]}")

    return err(req_id, -32601, f"未知方法: {method}")


if __name__ == "__main__":
    print("[ontoderive-unified-mcp v3] 启动: 11工具就绪", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            print(resp, flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(err(None, -32603, str(e)), flush=True)
