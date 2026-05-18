"""
OntoDerive 共享工具函数
=======================
消除各模块重复的 rf/wf/all_md/load_json/save_json 拷贝。
所有引擎模块从这里导入，不自己实现文件读写。
"""
import json
from collections import defaultdict
from pathlib import Path


def rf(path):
    """读文件，文件不存在返回空串"""
    p = Path(path) if isinstance(path, str) else path
    return p.read_text("utf-8", errors="ignore") if p.exists() else ""


def wf(path, text):
    """写文件，自动创建父目录"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def all_md(directory):
    """列出目录下所有 .md 文件，按路径排序"""
    dp = Path(directory)
    return sorted(dp.rglob("*.md")) if dp.exists() else []


def load_json(path):
    """加载JSON文件，失败返回None"""
    p = Path(path)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_json(path, data):
    """保存JSON文件，自动创建父目录"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def detect_cycles(nodes, edges):
    """
    共享的三色DFS环检测算法。
    nodes: dict {id: info} 或 set of ids
    edges: dict {from_id: [to_id]} 或 defaultdict(list)
    返回检测到的环列表。
    """
    node_ids = set(nodes.keys()) if isinstance(nodes, dict) else set(nodes)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in node_ids}
    cycles = []

    def dfs(u, path):
        color[u] = GRAY
        path.append(u)
        for v in edges.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                cycle_start = path.index(v)
                cycles.append(path[cycle_start:] + [v])
            elif color[v] == WHITE:
                dfs(v, path)
        path.pop()
        color[u] = BLACK

    for n in node_ids:
        if color.get(n) == WHITE:
            dfs(n, [])
    return cycles

