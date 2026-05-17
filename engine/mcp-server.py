#!/usr/bin/env python3
"""
OntoDerive MCP Server — AI agent 可直接调用的推导引擎
========================================================
提供三个工具给AI agent使用:
  - ontoderive_init: 初始化新项目
  - ontoderive_derive: 执行正向推导
  - ontoderive_check: 执行规约检查
  - ontoderive_rounds: 多轮迭代

用法:
    python3 mcp-server.py    # 启动MCP server(stdio模式)

依赖: Python 3.8+, 无需外部MCP库(使用stdio JSON-RPC协议)
"""
import datetime, json, os, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "engine"))
from derive import OntoDerive

def handle_request(req):
    """处理JSON-RPC请求"""
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    if method == "tools/list":
        return respond(req_id, {
            "tools": [
                {
                    "name": "ontoderive_init",
                    "description": "初始化一个新的OntoDerive项目骨架(创建facts/entities/inferences/scheme目录)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "项目名称"}
                        },
                        "required": ["name"]
                    }
                },
                {
                    "name": "ontoderive_derive",
                    "description": "正向推导：扫描项目的事实/实体/推论文件，生成推导摘要",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "项目路径"}
                        }
                    }
                },
                {
                    "name": "ontoderive_check",
                    "description": "规约检查：执行8条规约(事实完整性/断言追溯/可证伪性/ID合规等)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "项目路径"}
                        }
                    }
                },
                {
                    "name": "ontoderive_rounds",
                    "description": "多轮迭代：执行推导→检查→报告的收敛循环",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "项目路径"},
                            "rounds": {"type": "number", "description": "迭代轮数"}
                        }
                    }
                },
                {
                    "name": "ontoderive_generate",
                    "description": "生成推导报告(markdown格式)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project": {"type": "string", "description": "项目路径"}
                        }
                    }
                }
            ]
        })

    elif method == "tools/call":
        tool = params.get("name", "")
        args = params.get("arguments", {})
        project = args.get("project", ".")
        name = args.get("name", "demo")
        rounds = args.get("rounds", 3)

        if tool == "ontoderive_init":
            od = OntoDerive(name)
            od.derive()
            return respond(req_id, {"output": f"项目'{name}'已初始化"})

        elif tool in ("ontoderive_derive", "ontoderive_check", "ontoderive_generate"):
            od = OntoDerive(project)
            if tool == "ontoderive_derive":
                result = od.derive()
            elif tool == "ontoderive_check":
                result = od.check()
            else:
                result = od.generate_report()
            return respond(req_id, {"output": str(result)[:500]})

        elif tool == "ontoderive_rounds":
            od = OntoDerive(project)
            od.run_rounds(rounds)
            return respond(req_id, {"output": f"{rounds}轮迭代完成"})

        return error(req_id, -32601, f"未知工具: {tool}")

    elif method == "initialize":
        return respond(req_id, {
            "protocolVersion": "0.1.0",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ontoderive-mcp", "version": "1.2.0"}
        })

    return error(req_id, -32601, f"未知方法: {method}")

def respond(req_id, result):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}, ensure_ascii=False)

def error(req_id, code, message):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}, ensure_ascii=False)

if __name__ == "__main__":
    print("[ontoderive-mcp] 启动中...", file=sys.stderr)
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            print(resp, flush=True)
        except json.JSONDecodeError:
            continue
