"""Tests for ToolForge MCP server shim — 委托至统一MCP"""
import json

from engine.toolforge.mcp_server import handle_request


def test_can_import():
    from engine.toolforge import mcp_server
    assert mcp_server is not None


def test_handle_request_exists():
    """验证 handle_request 是来自统一MCP server的可调用对象"""
    assert callable(handle_request)


def test_handle_request_initialize():
    """验证MCP server能处理 initialize 请求"""
    resp = handle_request({"method": "initialize", "id": 1, "params": {}})
    assert resp is not None
    data = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in data or "error" in data


def test_handle_request_tools_list():
    """验证MCP server能返回工具列表"""
    resp = handle_request({"method": "tools/list", "id": 1})
    assert resp is not None
    data = json.loads(resp) if isinstance(resp, str) else resp
    assert "result" in data
    assert "tools" in data["result"]
