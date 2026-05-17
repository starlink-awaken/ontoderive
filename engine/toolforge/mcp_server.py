#!/usr/bin/env python3
"""
ToolForge MCP Server — AI agent 可调用的思维工具匹配服务
=========================================================
提供三个工具给 AI agent 使用:
  - toolforge_match: 按目标+上下文匹配思维工具（按类别分组）
  - toolforge_select: 跨类别选择 Top-N 工具
  - toolforge_guide: 生成 OntoDerive 推导指导

用法:
    python3 engine/toolforge/mcp_server.py    # 启动 MCP server (stdio 模式)

注册到 Agora:
    agora register toolforge --mcp "python3 engine/toolforge/mcp_server.py" --port 9003

依赖: Python 3.8+, 无需外部库（stdio JSON-RPC 协议）
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from engine.toolforge import ToolForge


def respond(req_id, result):
    """构建 JSON-RPC 响应"""
    return json.dumps(
        {"jsonrpc": "2.0", "id": req_id, "result": result}, ensure_ascii=False
    )


def error(req_id, code, message):
    """构建 JSON-RPC 错误响应"""
    return json.dumps(
        {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}},
        ensure_ascii=False,
    )


def handle_request(req, forge):
    """处理 JSON-RPC 请求"""
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    if method == "tools/list":
        return respond(
            req_id,
            {
                "tools": [
                    {
                        "name": "toolforge_match",
                        "description": "按目标描述和上下文关键词匹配思维工具（方法论/策略/模式/原则/理论/技能），按类别分组返回",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "goal": {
                                    "type": "string",
                                    "description": "目标描述，如'分析新能源汽车市场'",
                                },
                                "context": {
                                    "type": "string",
                                    "description": "上下文/领域关键词，如'竞争,政策,政府'",
                                },
                            },
                            "required": ["goal"],
                        },
                    },
                    {
                        "name": "toolforge_select",
                        "description": "跨类别选择 Top-N 最匹配的思维工具，返回扁平列表",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "goal": {
                                    "type": "string",
                                    "description": "目标描述",
                                },
                                "context": {
                                    "type": "string",
                                    "description": "上下文/领域关键词",
                                },
                                "top_n": {
                                    "type": "integer",
                                    "description": "返回数量，默认5",
                                    "default": 5,
                                },
                            },
                            "required": ["goal"],
                        },
                    },
                    {
                        "name": "toolforge_guide",
                        "description": "生成 OntoDerive 推导指导：将匹配的工具映射为具体的推导步骤和文件建议",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "goal": {
                                    "type": "string",
                                    "description": "目标描述",
                                },
                                "context": {
                                    "type": "string",
                                    "description": "上下文/领域关键词",
                                },
                            },
                            "required": ["goal"],
                        },
                    },
                ]
            },
        )

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "toolforge_match":
                goal = arguments.get("goal", "")
                context = arguments.get("context", "")
                result = forge.match(goal, context)
                return respond(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2),
                            }
                        ]
                    },
                )

            elif tool_name == "toolforge_select":
                goal = arguments.get("goal", "")
                context = arguments.get("context", "")
                top_n = arguments.get("top_n", 5)
                result = forge.select(goal, context, top_n)
                return respond(
                    req_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    [
                                        {
                                            "id": t["id"],
                                            "name": t["name"],
                                            "score": t["score"],
                                            "description": t["description"],
                                            "applies_to": t["applies_to"],
                                        }
                                        for t in result
                                    ],
                                    ensure_ascii=False,
                                    indent=2,
                                ),
                            }
                        ]
                    },
                )

            elif tool_name == "toolforge_guide":
                goal = arguments.get("goal", "")
                context = arguments.get("context", "")
                result = forge.to_inference_guide(goal, context)
                return respond(
                    req_id, {"content": [{"type": "text", "text": result}]}
                )

            else:
                return error(req_id, -32601, f"Unknown tool: {tool_name}")

        except Exception as e:
            return error(req_id, -32000, str(e))

    elif method == "initialize":
        return respond(
            req_id,
            {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "toolforge",
                    "version": "1.0.0",
                },
                "capabilities": {"tools": {}},
            },
        )

    else:
        return error(req_id, -32601, f"Unknown method: {method}")


def main():
    forge = ToolForge()
    sys.stderr.write("[toolforge-mcp] ToolForge MCP Server 已启动 (stdio)\n")
    sys.stderr.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req, forge)
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            sys.stderr.write(f"[toolforge-mcp] JSON parse error\n")
            sys.stderr.flush()
        except Exception as e:
            sys.stderr.write(f"[toolforge-mcp] Error: {e}\n")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
