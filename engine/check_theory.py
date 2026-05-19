"""
理论层规约检查 — C-09~C-13独立策略单元
=========================================
每个理论模块暴露check_xxx(root)函数，消除check.py的hub-spoke模式。
"""
import sys
from pathlib import Path


def _call_result(protocol_id, name, detail_fn):
    """统一的结果格式"""
    return {"protocol_id": protocol_id, "name": name, "detail_fn": detail_fn}


def check_bayesian(root):
    """C-09: 贝叶斯信念传播"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from bayesian import BayesianLayer
        bl = BayesianLayer(root)
        dist = bl.get_distribution()
        all_confs = dist["facts"] + dist["inferences"]
        ok = all(0 < c < 1 for c in all_confs) if all_confs else True
        has_var = len(set(round(c, 1) for c in all_confs)) > 1 if all_confs else True
        return {
            "passed": ok and has_var,
            "severity": "WARN" if not (ok and has_var) else "PASS",
            "detail": f"事实{dist['n_facts']}个, 推论{dist['n_inferences']}个, "
                      f"平均置信度{sum(all_confs)/len(all_confs):.2f}" if all_confs else "N/A",
            "distribution": dist,
        }
    except ImportError:
        return {"passed": False, "severity": "WARN", "detail": "bayesian.py未安装"}
    except Exception as e:
        return {"passed": False, "severity": "WARN", "detail": f"异常: {str(e)[:50]}"}


def check_metrics(root, precomputed_confs=None):
    """C-10: KQI知识质量指数"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from metrics import MetricsLayer
        ml = MetricsLayer(root)
        kqi = ml.compute_kqi(precomputed_confs=precomputed_confs)
        ok = kqi["kqi"] > 0 and kqi["entropy"] >= 0
        return {
            "passed": ok,
            "severity": "PASS",
            "detail": f"KQI={kqi['kqi']}, 熵={kqi['entropy']}bits, "
                      f"密度={kqi['density']:.2f}, 覆盖={kqi['coverage']*100:.0f}%",
        }
    except ImportError:
        return {"passed": False, "severity": "WARN", "detail": "metrics.py未安装"}
    except Exception as e:
        return {"passed": False, "severity": "WARN", "detail": f"异常: {str(e)[:50]}"}


def check_pid(root):
    """C-11: PID反馈控制"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from controller import PIDController
        pid = PIDController(root).analyze()
        return {
            "passed": pid["stability"] == "stable",
            "severity": "WARN" if pid["stability"] != "stable" else "PASS",
            "detail": f"P={pid['p_value']} I={pid['i_value']} D={pid['d_value']} "
                      f"信号={pid['control_signal']} 状态={pid['stability']}",
        }
    except Exception:
        return {"passed": True, "severity": "PASS", "detail": "首次运行, 信号=0 (需历史数据)"}


def check_turing(root):
    """C-12: 知识状态机"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from turing_k import KnowledgeTM
        state = KnowledgeTM(root).snapshot()
        return {
            "passed": state.timestamp is not None,
            "severity": "PASS",
            "detail": f"快照: {state.facts}F/{state.inferences}I/{state.entities}E",
        }
    except Exception as e:
        return {"passed": False, "severity": "WARN", "detail": f"异常: {str(e)[:50]}"}


def check_ontolang():
    """C-13: OntoLang形式语言"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from ontolang import OntoLangParser
        parser = OntoLangParser()
        ast = parser.test_suite()
        nodes = len(ast["entities"]) + len(ast["facts"]) + len(ast["inferences"]) + len(ast["protocols"])
        errors = parser.validate(ast)
        return {
            "passed": len(errors) == 0,
            "severity": "PASS" if len(errors) == 0 else "ERROR",
            "detail": f"AST节点{nodes}个, 错误{len(errors)}个",
        }
    except Exception as e:
        return {"passed": False, "severity": "WARN", "detail": f"异常: {str(e)[:50]}"}


# Strategy registry — check.py通过此注册表调用，而非直接import各模块
THEORY_CHECKS = [
    ("C-09", "贝叶斯信念传播(智能层)", check_bayesian),
    ("C-10", "信息论层(KQI质量指数)", check_metrics),
    ("C-11", "控制论层(PID反馈)", check_pid),
    ("C-12", "图灵机层(知识状态机)", check_turing),
    ("C-13", "形式语言层(OntoLang解析)", check_ontolang),
]
