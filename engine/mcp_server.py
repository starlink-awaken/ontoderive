#!/usr/bin/env python3
"""
OntoDerive Unified MCP Server v3.6.4
====================================
统一入口：17工具 (推导5 + 匹配3 + 分析3 + 导出2 + 配置1 + 写入3)
协议：JSON-RPC 2.0 over stdio
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # 项目根
sys.path.insert(0, str(Path(__file__).parent))  # engine/

from engine.mcp_handlers import TOOL_DEFS, handle_request, err  # noqa: I001


def main():
    """启动MCP server (stdio模式)"""
    n_tools = len(TOOL_DEFS)
    print(f"[ontoderive-unified-mcp v3] 启动: {n_tools}工具就绪", file=sys.stderr)
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


if __name__ == "__main__":
    main()
