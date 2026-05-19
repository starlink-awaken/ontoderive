"""LLM智能层 — 推理增强 + 洞察 + 评估 + 提示词工程"""
from engine.llm import LLMEnhancer, get_enhancer
from engine.insight import InsightEngine, Insight, InsightCache
from engine.judge import OntoDeriveJudge, JudgeResult
from engine.prompts import PromptTemplate, get_template, DOMAIN_PRESETS, auto_detect_domain
