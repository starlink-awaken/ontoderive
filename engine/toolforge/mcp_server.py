#!/usr/bin/env python3
"""
ToolForge MCP Server — 委托给统一 ontoderive MCP server
=========================================================
仅保留兼容性入口，实际逻辑由 engine/mcp-server.py 统一处理。
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from mcp_server import handle_request

if __name__ == "__main__":
    sys.stderr.write("[toolforge-mcp] 委托至统一ontoderive MCP server v3\n")
    sys.stderr.flush()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(resp + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except Exception as e:
            sys.stderr.write(f"[toolforge-mcp] Error: {e}\n")
            sys.stderr.flush()
