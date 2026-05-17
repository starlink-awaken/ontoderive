"""
OntoDerive 图灵机层 — 知识状态机(K-TM)
=========================================
将推导过程建模为图灵机: 每次derive产生新状态,状态间差异即"学到了什么"。

用法:
    from engine.turing_k import KnowledgeTM
    ktm = KnowledgeTM(project_root)
    ktm.snapshot()       # 创建当前知识快照
    ktm.diff()           # 显示上次到这次的差异
    ktm.replay()         # 回放所有推导步骤
"""
import datetime, json, hashlib
from pathlib import Path

class KnowledgeTM:
    def __init__(self, project_root):
        self.root = Path(project_root)
        self.log_dir = self.root / "_derivation_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def snapshot(self):
        """创建当前知识状态快照"""
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "files": {},
        }
        for f in sorted((self.root).rglob("*.md")):
            if "_derivation_logs" in str(f):
                continue
            text = f.read_text("utf-8", errors="ignore")
            state["files"][str(f.relative_to(self.root))] = {
                "size": len(text),
                "hash": hashlib.md5(text.encode()).hexdigest()[:8],
            }

        snapshot_path = self.log_dir / f"snapshot-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        (self.log_dir / "latest-snapshot.json").write_text(
            json.dumps({"timestamp": state["timestamp"], "file_count": len(state["files"])},
                      ensure_ascii=False, indent=2))
        print(f"[turing] ✅ 快照: {len(state['files'])}文件, {state['timestamp']}")
        return state

    def diff(self):
        """比较最新两次快照"""
        snapshots = sorted(self.log_dir.glob("snapshot-*.json"))
        if len(snapshots) < 2:
            print("[turing] ℹ️ 需要至少2次快照才能对比")
            return []

        import json
        old = json.loads(snapshots[-2].read_text())
        new = json.loads(snapshots[-1].read_text())

        changes = []
        old_files = old.get("files", {})
        new_files = new.get("files", {})

        for fname, info in new_files.items():
            if fname not in old_files:
                changes.append({"file": fname, "type": "added", "size": info["size"]})
            elif old_files[fname]["hash"] != info["hash"]:
                changes.append({"file": fname, "type": "modified", "size": info["size"]})

        for fname in old_files:
            if fname not in new_files:
                changes.append({"file": fname, "type": "removed"})

        print(f"[turing] 📊 差异: {len(changes)}处变更")
        for c in changes[:10]:
            print(f"  {c['type']:8s} {c['file']}")
        return changes

    def replay(self):
        """回放推导步骤(列出所有快照时间线)"""
        snapshots = sorted(self.log_dir.glob("snapshot-*.json"))
        print(f"[turing] 📜 推导时间线({len(snapshots)}步):")
        for i, s in enumerate(snapshots):
            try:
                data = json.loads(s.read_text())
            except: continue
            ts = data.get("timestamp", "unknown")[:19]
            fc = len(data.get("files", {}))
            print(f"  q{i}: [{ts}] {fc}文件")
        return snapshots
