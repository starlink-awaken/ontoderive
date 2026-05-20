"""MCP服务器测试"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "engine"))

from mcp_server import handle_request, TOOL_DEFS


def test_tools_list():
    resp = json.loads(handle_request({"id": 1, "method": "tools/list"}))
    tools = resp["result"]["tools"]
    assert len(tools) == 14
    names = [t["name"] for t in tools]
    assert "ontoderive_init" in names
    assert "ontoderive_derive" in names
    assert "ontoderive_check" in names
    assert "toolforge_match" in names
    assert "toolforge_select" in names
    assert "toolforge_guide" in names
    assert "ontoderive_analyze" in names


def test_initialize():
    resp = json.loads(handle_request({"id": 2, "method": "initialize"}))
    assert resp["result"]["serverInfo"]["name"] == "ontoderive-unified-mcp"
    assert resp["result"]["serverInfo"]["version"] == "3.5.0"
    assert "tools" in resp["result"]["capabilities"]


def test_unknown_method():
    resp = json.loads(handle_request({"id": 3, "method": "unknown"}))
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_toolforge_select():
    resp = json.loads(handle_request({
        "id": 4, "method": "tools/call",
        "params": {"name": "toolforge_select", "arguments": {"goal": "分析市场", "top_n": 3}}
    }))
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in result


def test_toolforge_guide():
    resp = json.loads(handle_request({
        "id": 5, "method": "tools/call",
        "params": {"name": "toolforge_guide", "arguments": {"goal": "分析市场"}}
    }))
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in result or "error" in result


def test_ontoderive_check():
    resp = json.loads(handle_request({
        "id": 6, "method": "tools/call",
        "params": {"name": "ontoderive_check", "arguments": {"project": "examples/z-park"}}
    }))
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in result


def test_ontoderive_config():
    resp = json.loads(handle_request({
        "id": 7, "method": "tools/call",
        "params": {"name": "ontoderive_config", "arguments": {"project": "."}}
    }))
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in result


def test_unknown_tool():
    resp = json.loads(handle_request({
        "id": 8, "method": "tools/call",
        "params": {"name": "nonexistent_tool", "arguments": {}}
    }))
    result = json.loads(resp) if isinstance(resp, str) else resp
    assert "error" in result


def test_tool_defs_schemas():
    for t in TOOL_DEFS:
        assert "name" in t
        assert "description" in t
        assert "inputSchema" in t
        assert "type" in t["inputSchema"]
