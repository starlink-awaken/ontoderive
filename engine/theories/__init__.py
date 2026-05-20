"""六论融合层 — 贝叶斯/信息论/控制论/图灵机/逻辑/形式语言"""
from engine.theories.bayesian import BayesianLayer, BayesianNetwork
from engine.theories.metrics import MetricsLayer
from engine.theories.controller import PIDController
from engine.theories.logic import EntailmentGraph, build_from_project
from engine.theories.turing_k import KnowledgeTM
from engine.theories.ontolang import OntoLangParser
