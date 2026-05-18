"""
OntoDerive 逻辑层 — 蕴含图分析
===============================
构建知识库的有向图模型，支持：
- 推导链分析（最长/最短/平均深度）
- 循环引用检测
- 瓶颈节点、冗余路径检测
- GraphML导出用于可视化
"""
from collections import defaultdict
try:
    from .utils import detect_cycles
except ImportError:
    from utils import detect_cycles  # noqa


class EntailmentGraph:
    """蕴含图：节点=事实+推论，边=derives_from"""

    def __init__(self):
        self.nodes = {}       # id -> {type(fact|inference), label}
        self.edges = defaultdict(list)   # from -> [to]
        self.reverse = defaultdict(list)  # to -> [from]

    def add_node(self, nid, ntype="fact", label=""):
        self.nodes[nid] = {"type": ntype, "label": label}
        self.edges.setdefault(nid, [])

    def add_edge(self, from_id, to_id):
        if from_id in self.nodes and to_id in self.nodes:
            self.edges[from_id].append(to_id)
            self.reverse[to_id].append(from_id)

    def detect_cycles(self):
        return detect_cycles(self.nodes, self.edges)

    def chain_depths(self):
        """计算每个节点的推导链深度（从根事实出发的最长路径）"""
        roots = [n for n, info in self.nodes.items() if info["type"] == "fact" and not self.reverse.get(n)]
        depth = {}
        visited = set()

        def dfs(u, d):
            depth[u] = max(depth.get(u, 0), d)
            if u in visited:
                return
            visited.add(u)
            for v in self.edges.get(u, []):
                dfs(v, d + 1)

        for r in roots:
            dfs(r, 0)

        if not depth:
            return {"max": 0, "min": 0, "avg": 0, "per_node": {}}

        depths = list(depth.values())
        return {
            "max": max(depths),
            "min": min(depths),
            "avg": round(sum(depths) / len(depths), 2),
            "per_node": {n: d for n, d in depth.items()},
        }

    def bottlenecks(self):
        """检测瓶颈节点（出度最高的前5个）"""
        if not self.edges:
            return []
        out_degrees = [(n, len(v)) for n, v in self.edges.items()]
        out_degrees.sort(key=lambda x: x[1], reverse=True)
        return [{"node": n, "out_degree": d, "label": self.nodes[n]["label"]} for n, d in out_degrees[:5] if d > 0]

    def redundant_paths(self):
        """检测冗余路径（同一对节点间存在多条路径）"""
        redundant = []
        checked = set()
        for u in self.nodes:
            for v in self.nodes:
                if u == v or (u, v) in checked:
                    continue
                checked.add((u, v))
                paths = self._find_paths(u, v, max_paths=3)
                if len(paths) > 1:
                    redundant.append({"from": u, "to": v, "path_count": len(paths), "paths": paths})
        return redundant[:10]

    def _find_paths(self, start, end, max_paths=3):
        paths = []

        def dfs(u, path, visited):
            if len(paths) >= max_paths:
                return
            if u == end and len(path) > 0:
                paths.append(path + [u])
                return
            for v in self.edges.get(u, []):
                if v not in visited:
                    dfs(v, path + [u], visited | {v})

        dfs(start, [], {start})
        return paths

    def to_graphml(self):
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
                 '  <graph id="entailment" edgedefault="directed">']
        for nid, info in self.nodes.items():
            lines.append(f'    <node id="{nid}"><data key="label">{info["label"]}</data><data key="type">{info["type"]}</data></node>')
        edge_id = 0
        for u in self.nodes:
            for v in self.edges.get(u, []):
                lines.append(f'    <edge id="e{edge_id}" source="{u}" target="{v}"/>')
                edge_id += 1
        lines.append('  </graph>')
        lines.append('</graphml>')
        return '\n'.join(lines)

    def stats(self):
        cycles = self.detect_cycles()
        depths = self.chain_depths()
        bn = self.bottlenecks()
        fact_count = sum(1 for n in self.nodes.values() if n["type"] == "fact")
        inf_count = sum(1 for n in self.nodes.values() if n["type"] == "inference")

        return {
            "nodes": len(self.nodes),
            "facts": fact_count,
            "inferences": inf_count,
            "edges": sum(len(v) for v in self.edges.values()),
            "roots": fact_count,
            "cycles": len(cycles),
            "has_cycles": len(cycles) > 0,
            "max_depth": depths["max"],
            "avg_depth": depths["avg"],
            "bottlenecks": bn,
        }


def build_from_project(project_root):
    """从OntoDerive项目目录构建蕴含图"""
    import re
    from pathlib import Path
    try:
        from .utils import rf, all_md
    except ImportError:
        from utils import rf, all_md  # noqa

    root = Path(project_root)
    graph = EntailmentGraph()

    # 扫描事实
    fact_ids = set()
    for f in all_md(root / "facts"):
        text = rf(f)
        for m in re.finditer(r'(D-F\d+|P-F\d+)', text):
            fid = m.group(0)
            if fid not in graph.nodes:
                graph.add_node(fid, "fact", fid)
                fact_ids.add(fid)

    # 扫描推论
    for f in all_md(root / "inferences"):
        text = rf(f)
        blocks = re.split(r'^##\s+', text, flags=re.MULTILINE)
        for block in blocks[1:]:
            title = block.strip().split("\n")[0].strip()
            df = re.findall(r'(D-F\d+|P-F\d+)', block)
            if title not in graph.nodes:
                graph.add_node(title, "inference", title[:80])
            for src in df:
                if src not in graph.nodes:
                    graph.add_node(src, "fact", src)
                graph.add_edge(src, title)

    return graph
