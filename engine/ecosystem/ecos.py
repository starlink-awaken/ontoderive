"""
OntoDerive 生态适配器 — eCOS事件发布/订阅
==========================================
Pipeline每阶段完成后向eCOS发布事件。
"""
import json
import datetime


class ECOSObserver:
    """eCOS可观察的Pipeline事件发布者"""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.events = []

    def on_stage_start(self, stage: str, context: dict):
        event = {
            "@type": "PipelineStageStarted",
            "stage": stage,
            "timestamp": datetime.datetime.now().isoformat(),
            "project": context.get("project_root", ""),
        }
        self.events.append(event)
        self._emit(event)

    def on_stage_end(self, stage: str, result: dict):
        event = {
            "@type": "PipelineStageCompleted",
            "stage": stage,
            "timestamp": datetime.datetime.now().isoformat(),
            "result_summary": str(result)[:200],
        }
        self.events.append(event)
        self._emit(event)

    def on_error(self, stage: str, error: Exception):
        event = {
            "@type": "PipelineError",
            "stage": stage,
            "timestamp": datetime.datetime.now().isoformat(),
            "error": str(error),
        }
        self.events.append(event)
        self._emit(event)

    def _emit(self, event):
        if self.output_dir:
            from pathlib import Path
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)
            log_path = Path(self.output_dir) / "pipeline-events.jsonl"
            with open(log_path, "a") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def get_events(self):
        return self.events


def create_observer(output_dir=None):
    return ECOSObserver(output_dir)
