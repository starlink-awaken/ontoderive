"""
ToolForge — 思维工具匹配模块（原 MindForge，已并入 OntoDerive）
=============================================================
输入: 目标描述 + 上下文关键词
输出: 匹配的方法论/策略/模式/原则/理论/技能 + 使用建议

用法:
    python3 -m ontoderive.engine.toolforge.matcher "分析新能源汽车市场"
    python3 -m ontoderive.engine.toolforge.matcher --goal "设计数字化平台" --context "政府,教育"
"""

import json
from pathlib import Path

CATALOG_PATH = Path(__file__).parent / "catalog.json"


class ToolForge:
    """思维工具匹配引擎 — OntoDerive 前置模块"""

    def __init__(self, catalog_path=None):
        path = Path(catalog_path) if catalog_path else CATALOG_PATH
        self.catalog = json.loads(path.read_text()) if path.exists() else {"tools": []}

    def match(self, goal, context="", limit=3):
        """根据目标+上下文匹配工具，返回按类别分组的结果"""
        search_text = f"{goal} {context}".lower()
        results = {
            "methodologies": [],
            "strategies": [],
            "patterns": [],
            "principles": [],
            "theories": [],
            "skills": [],
        }

        for tool in self.catalog.get("tools", []):
            score = 0
            matched_keywords = []
            for kw in tool.get("keywords", []):
                if kw.lower() in search_text:
                    score += 1
                    matched_keywords.append(kw)

            # 标题部分匹配额外加分
            name_chars = [c for c in tool["name"] if c in search_text]
            if len(name_chars) >= 2:
                score += 0.5

            if score > 0:
                category = tool["category"]
                if category in results:
                    results[category].append(
                        {
                            "id": tool["id"],
                            "name": tool["name"],
                            "score": round(score, 1),
                            "matched": matched_keywords,
                            "description": tool.get("description", ""),
                            "applies_to": tool.get("applies_to", ""),
                            "source": tool.get("source", ""),
                        }
                    )

        for cat in results:
            results[cat].sort(key=lambda t: t["score"], reverse=True)
            results[cat] = results[cat][:limit]

        return results

    def select(self, goal, context="", top_n=5):
        """返回跨类别的 Top-N 工具列表（扁平排序）"""
        matched = self.match(goal, context)
        all_tools = []
        for cat_tools in matched.values():
            all_tools.extend(cat_tools)
        all_tools.sort(key=lambda t: t["score"], reverse=True)
        return all_tools[:top_n]

    def to_ontoderive(self, goal, context=""):
        """输出为 OntoDerive 兼容的推导框架约束"""
        matched = self.match(goal, context)
        lines = [f"# ToolForge 思维工具匹配 — {goal}", ""]

        for category, tools in matched.items():
            if not tools:
                continue
            cat_name = self.catalog.get("categories", {}).get(category, category)
            lines.append(f"## {category} — {cat_name}")
            for t in tools:
                lines.append(f"\n### {t['id']}: {t['name']} (匹配度: {t['score']})")
                lines.append(f"- 描述: {t['description']}")
                lines.append(f"- 适用: {t['applies_to']}")
                if t.get("source"):
                    lines.append(f"- 来源: {t['source']}")
                lines.append(f"- 匹配关键词: {', '.join(t['matched'])}")
            lines.append("")
        return "\n".join(lines)

    def to_inference_guide(self, goal, context=""):
        """生成 OntoDerive 推导指导：将匹配的工具映射为推导建议"""
        matched = self.match(goal, context)
        lines = [
            "# ToolForge → OntoDerive 推导指导",
            f"## 目标: {goal}",
            f"## 上下文: {context or '未指定'}",
            "",
            "## 推荐推导框架",
        ]

        framework_map = {
            "M-001": "使用波特五力框架分解 facts/competitive.md，识别五力要素 → 推论竞争格局",
            "M-002": "使用SWOT框架，在 inferences/ 中分别建立优势、劣势、机会、威胁推论",
            "M-003": "使用C-T-F七阶演绎，从核心矛盾出发逐层推导方案",
            "M-004": "使用金字塔原理组织 scheme/ 的结构，结论先行",
            "M-005": "在 facts/policy.md 中按P-E-S-T四维度建立宏观环境事实表",
            "M-006": "使用TOGAF的BDAT四层建立 scheme/architecture/ 的结构",
            "M-007": "在 entities/stakeholders.md 中建立利益相关者权力-利益矩阵",
            "M-008": "使用ADDIE五阶段设计 scheme/curriculum/ 的培训方案结构",
            "M-009": "在 inferences/business-model.md 中推导九要素商业模式",
            "M-010": "在 inferences/policy-window.md 中分析问题流、政策流、政治流的汇合时机",
            "S-001": "在 inferences/strategy.md 中推导差异化路径",
            "S-002": "在 facts/cost.md 中建立成本结构事实表，推导成本优势策略",
            "S-003": "在 inferences/market-first.md 中推导先市场后技术的验证路径",
            "S-004": "使用平台策略框架，在 inferences/platform.md 中推导平台增长模型",
            "S-005": "在 inferences/incremental.md 中记录渐进式推进的阶段划分和调整机制",
            "S-006": "在 facts/industry-education.md 中建立产业需求-教育资源匹配表",
            "S-007": "在 facts/cluster.md 中建立区域产业链和配套能力事实表",
            "S-008": "在 inferences/lean-startup.md 中建立构建-测量-学习循环模型",
            "P-001": "在 inferences/flywheel.md 中建立飞轮增强回路模型",
            "P-002": "在 scheme/ 中分别设计探索性单元和利用性单元",
            "P-006": "在 entities/innovation-system.md 中建立大学-产业-政府三方角色和互动关系模型",
            "P-007": "在 scheme/incubator.md 中设计孵化服务链（空间→资金→导师→网络）",
            "P-008": "在 inferences/tech-transfer.md 中推导技术转移路径和产业化方案",
            "T-001": "在 inferences/bayesian.md 中标注每个关键推论的先验概率和后验更新",
            "T-002": "在 inferences/game-theory.md 中建立多主体博弈矩阵",
            "T-003": "在 inference 中标注系统层次关系，使用系统论的整体涌现原则",
            "T-006": "在 facts/ 中增加制度环境事实表，推导制度约束对方案的影响",
            "T-008": "在 facts/cluster.md 中按钻石模型四要素建立产业集群竞争事实表",
            "T-009": "在 inferences/diffusion.md 中建立创新扩散S曲线和采纳者分类",
            "T-010": "在 scheme/learning.md 中基于建构主义设计情境化学习环境",
            "T-011": "在 entities/regional-innovation.md 中建立各创新主体和制度环境的实体关系",
            "T-012": "在 facts/technology.md 中对关键技术标注TRL等级并推导成熟路径",
            "PR-001": "每个推论必须以具体事实为支撑，标注来源引用",
            "PR-002": "在 inferences/first-principles.md 中记录从根本原理出发的推导链",
            "PR-005": "在 inferences/public-value.md 中评估方案对公共价值的贡献度和可问责性",
            "PR-006": "在 facts/ 中为每个关键决策标注证据等级（强/中/弱）和来源",
            "SK-005": "在 inferences/policy-options.md 中建立政策方案比较矩阵",
            "SK-007": "在 scheme/project-plan.md 中建立WBS分解和里程碑计划",
        }

        for category, tools in matched.items():
            for t in tools:
                tid = t["id"]
                if tid in framework_map:
                    lines.append(f"- **{t['name']}** ({t['id']}): {framework_map[tid]}")

        return "\n".join(lines)

    def report(self, goal, context=""):
        """终端输出匹配报告"""
        matched = self.match(goal, context)
        print(f"\n{'═' * 50}")
        print(f"  ToolForge 思维工具匹配")
        print(f"  目标: {goal}")
        if context:
            print(f"  上下文: {context}")
        print(f"{'═' * 50}\n")

        total = 0
        for category, tools in matched.items():
            if not tools:
                continue
            cat_name = self.catalog.get("categories", {}).get(category, category)
            print(f"  📂 {category} — {cat_name}")
            for t in tools:
                desc = t["description"][:50]
                print(
                    f"    {t['id']} {t['name']} (匹配度:{t['score']}) — {desc}"
                )
                total += 1

        print(f"\n  共匹配 {total} 个工具")
        return matched


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ToolForge 思维工具匹配引擎")
    parser.add_argument("goal", nargs="?", default="", help="目标描述")
    parser.add_argument("--goal", dest="goal2", help="目标描述（命名参数）")
    parser.add_argument("--context", help="上下文/领域描述")
    parser.add_argument("--ontoderive", action="store_true", help="输出 OntoDerive 兼容格式")
    parser.add_argument(
        "--inference-guide", action="store_true", help="输出推导指导格式"
    )
    parser.add_argument("--top", type=int, default=5, help="Top-N 工具数")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    tf = ToolForge()
    goal = args.goal or args.goal2 or "分析"
    context = args.context or ""

    if args.inference_guide:
        print(tf.to_inference_guide(goal, context))
    elif args.ontoderive:
        print(tf.to_ontoderive(goal, context))
    elif args.json:
        print(json.dumps(tf.select(goal, context, args.top), ensure_ascii=False, indent=2))
    else:
        matched = tf.report(goal, context)
        if matched:
            print(
                "\n💡 使用建议: 将以上工具作为分析框架，"
                "在 OntoDerive 的 inferences/ 中建立对应的推导结构"
            )
