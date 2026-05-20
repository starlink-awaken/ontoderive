#!/usr/bin/env python3
"""
OntoDerive Unified MCP Server v3.5
====================================
统一入口：14工具 (推导5 + 匹配3 + 分析3 + 导出2 + 配置1)
协议：JSON-RPC 2.0 over stdio
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
    # ── 推导工具 (5) ──
    {"name": "ontoderive_init", "description": "初始化新OntoDerive项目骨架", "inputSchema": {"type": "object", "properties": {"name": {"type": "string", "description": "项目名称"}}, "required": ["name"]}},
    {"name": "ontoderive_derive", "description": "正向推导：含分析模式(A1-A9)+关系推理(R19)+推导链路trail", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_check", "description": "规约检查：13条规约(C-01~C-13)含贝叶斯/KQI/PID", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_rounds", "description": "多轮迭代：derive→check循环至收敛", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}, "rounds": {"type": "number", "description": "迭代轮数", "default": 3}}}},
    {"name": "ontoderive_generate", "description": "生成推导报告(markdown)", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    # ── 分析工具 (1+2新) ──
    {"name": "ontoderive_analyze", "description": "全量分析：Pipeline全流程(ToolForge+derive+check)，含匹配推荐+置信度+KQI+收敛", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径"}, "goal": {"type": "string", "description": "分析目标"}, "context": {"type": "string", "description": "上下文关键词"}}}},
    {"name": "ontoderive_config", "description": "获取当前配置项(匹配模式/阈值等)", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_delta", "description": "对比最近两次推导的状态差异", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    # ── 分析模式 (v3.5 NEW) ──
    {"name": "ontoderive_analytics", "description": "运行分析模式(A1-A9): 供给弹性/风险传导/代理问题/激励相容/补救规划/市场结构/博弈均衡/策略空间/信息生态", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}, "max_depth": {"type": "number", "description": "最大推理深度(0=纯规则,5=LLM)", "default": 1}}}},
    {"name": "ontoderive_relations", "description": "关系推理(R19): 传递性+逆关系+域约束, 输入项目路径", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}}}},
    {"name": "ontoderive_export", "description": "导出分析结果(html/json/jsonld/turtle)", "inputSchema": {"type": "object", "properties": {"project": {"type": "string", "description": "项目路径", "default": "."}, "format": {"type": "string", "description": "导出格式: html|json|jsonld|turtle", "default": "html"}}}},
    # ── 工具匹配 (3) ──
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

            # ── v3.5 新增工具 ──
            elif tool == "ontoderive_analytics":
                od = OntoDerive(project)
                r = od.derive()
                ae_conclusions = [c for c in r.get("derived_conclusions", [])
                                  if c.get("source") == "analytics"]
                return respond(req_id, {"analytics_count": len(ae_conclusions),
                                        "conclusions": ae_conclusions[:10]})

            elif tool == "ontoderive_relations":
                od = OntoDerive(project)
                r = od.derive()
                rel_conclusions = [c for c in r.get("derived_conclusions", [])
                                   if c.get("type", "").startswith("relation_")]
                return respond(req_id, {"relations_count": len(rel_conclusions),
                                        "conclusions": rel_conclusions[:10]})

            elif tool == "ontoderive_export":
                od = OntoDerive(project)
                r = od.derive()
                fmt = args.get("format", "html")
                if fmt in ("html", "json"):
                    from engine.core.export import to_html, to_json
                    output = to_html(r, project) if fmt == "html" else to_json(r)
                else:
                    from engine.formalize import Formalizer
                    from engine.foundation.ontology_map import OntologyMapper
                    fz = Formalizer()
                    kb = fz.extract_from_text(
                        "\n".join(str(r.get(k, "")) for k in r), mode="rule_only")
                    om = OntologyMapper()
                    output = om.export(kb, fmt=fmt)
                return respond(req_id, {"format": fmt, "output": output[:3000],
                                        "length": len(output)})

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
