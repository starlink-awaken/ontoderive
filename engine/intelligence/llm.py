"""
OntoDerive LLM增强层 — 零依赖降级 + 本地模型增强
===================================================
默认使用规则引擎（零依赖），当LLM可用时自动增强推导质量。
支持的LLM后端：ollama(本地), openai API, anthropic API
"""
import json
import os
from typing import Optional


class LLMEnhancer:
    """LLM增强器 — 失败时静默降级为规则引擎"""

    def __init__(self, backend="auto", model=None, base_url=None):
        if backend == "auto":
            backend = os.environ.get("ONTODERIVE_LLM_BACKEND", "auto")
        self.backend = self._detect_backend(backend)
        self.model = model or os.environ.get("ONTODERIVE_LLM_MODEL", "")
        self.base_url = base_url or os.environ.get("ONTODERIVE_LLM_URL", "")
        self.available = self._probe()

    def _detect_backend(self, backend):
        if backend != "auto":
            return backend
        if os.environ.get("OPENAI_API_KEY"): return "openai"
        if os.environ.get("ANTHROPIC_API_KEY"): return "anthropic"
        # 检测本地API (localhost:1234)
        try:
            import urllib.request
            import json
            req = urllib.request.Request("http://localhost:1234/api/v1/chat",
                data=json.dumps({"model": "qwopus3.6-35b-a3b-v1", "input": "hi"}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r:
                json.loads(r.read())
            self.base_url = "http://localhost:1234/api/v1/chat"
            if not self.model:
                self.model = os.environ.get("ONTODERIVE_LLM_MODEL", "qwopus3.6-35b-a3b-v1")
            return "local"
        except Exception:
            pass
        try:
            import subprocess
            r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0: return "ollama"
        except Exception:
            pass
        return "none"

    def _probe(self):
        if self.backend == "ollama":
            try:
                import subprocess
                r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=3)
                if r.returncode != 0:
                    return False
                models = r.stdout
                if self.model and self.model not in models:
                    return False
                if not self.model:
                    # 自动选模型：优先中文能力强的小模型
                    for m in ["qwen3.5:4b", "qwen2.5:7b", "qwen2.5:3b",
                               "gemma4:e2b", "qwen2.5:1.5b", "llama3.2:3b"]:
                        if m in models:
                            self.model = m
                            return True
                    # fallback: 用第一个可用模型
                    first_line = models.strip().split("\n")[1] if "\n" in models else ""
                    if first_line:
                        self.model = first_line.split()[0]
                        return True
                return self.model in models
            except Exception:
                return False
        if self.backend == "local":
            return True  # 自动检测时已验证连接
        if self.backend in ("openai", "anthropic"):
            return bool(os.environ.get(f"{self.backend.upper()}_API_KEY"))
        return False

    def _call_ollama(self, prompt, system="", temperature=0.3):
        import subprocess
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        r = subprocess.run(
            ["ollama", "run", self.model, full_prompt],
            capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0:
            return None
        return r.stdout.strip()

    def _call_openai(self, prompt, system="", temperature=0.3):
        try:
            from openai import OpenAI
            client = OpenAI(base_url=self.base_url or None)
            resp = client.chat.completions.create(
                model=self.model or "gpt-4o-mini",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                temperature=temperature, max_tokens=500
            )
            return resp.choices[0].message.content
        except Exception:
            return None

    def _call_local(self, prompt, system="", temperature=0.3):
        """本地OpenAI兼容API (localhost:1234, input/output格式)"""
        import urllib.request
        payload = {"model": self.model, "input": prompt}
        if system:
            payload["system_prompt"] = system
        try:
            req = urllib.request.Request(
                self.base_url or "http://localhost:1234/api/v1/chat",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            for item in data.get("output", []):
                if item.get("type") == "message":
                    return item.get("content", "").strip()
            return None
        except Exception:
            return None

    def _call(self, prompt, system="", temperature=0.3):
        if not self.available:
            return None
        try:
            if self.backend == "ollama":
                return self._call_ollama(prompt, system, temperature)
            elif self.backend == "openai":
                return self._call_openai(prompt, system, temperature)
            elif self.backend == "local":
                return self._call_local(prompt, system, temperature)
        except Exception:
            return None
        return None

    # ── 三个增强入口 ──

    def enhance_derivation_hints(self, facts_summary, inferences_text, existing_hints):
        """增强推导提示：LLM读取推论全文，生成洞察"""
        if not self.available or self.backend == "none":
            return existing_hints
        prompt = f"""分析以下推论，给出1-2条推导建议。每条20字以内。只输出建议，一行一条。

事实: {facts_summary}
推论:
{inferences_text[:1500]}"""
        result = self._call(prompt, "你是知识工程分析专家。简洁输出。", 0.3)
        if result:
            lines = [l.strip("- 1234567890.*# ") for l in result.split("\n") if l.strip() and len(l.strip()) > 4]
            return existing_hints + lines[:2]
        return existing_hints

    def detect_contradictions(self, inference_a, inference_b, shared_facts):
        """语义矛盾检测：LLM判断两个推论是否真正矛盾"""
        if not self.available or self.backend == "none":
            return None
        prompt = f"""判断以下两个推论是否存在实质性矛盾。仅回答YES或NO。

推论A: {inference_a[:200]}
推论B: {inference_b[:200]}
共享事实: {shared_facts}

是否存在矛盾？(YES/NO):"""
        result = self._call(prompt, "仅回答YES或NO。", 0.1)
        return result and "YES" in result.upper()

    def smart_match_tools(self, goal, context, tools_descriptions):
        """智能工具匹配：LLM替代TF-IDF做语义匹配"""
        if not self.available or self.backend == "none":
            return None
        tools_text = "\n".join(f"- {t['id']}: {t['name']} — {t.get('description','')[:60]}" for t in tools_descriptions[:30])
        prompt = f"""分析目标并从工具列表中选出最合适的3个工具ID。

目标: {goal}
上下文: {context}

工具列表:
{tools_text}

只输出3个工具ID，用逗号分隔（如 M-001, S-003, T-001）:"""
        result = self._call(prompt, "只输出工具ID，逗号分隔。", 0.1)
        if result:
            ids = [x.strip() for x in result.split(",")[:3]]
            return ids
        return None


# 模块级单例
_enhancer: Optional[LLMEnhancer] = None


def get_enhancer(force=False):
    global _enhancer
    if _enhancer is None or force:
        _enhancer = LLMEnhancer()
    return _enhancer
