"""OntoDerive CLI — pip install 入口点

用法:
    ontoderive init my-project
    ontoderive derive --project .
    ontoderive check --project .
    ontoderive toolforge "分析市场" --inference-guide
"""

import sys
from pathlib import Path

# 确保项目根目录可导入 engine 包
_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main():
    """统一 CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="OntoDerive v3.5.0 — 知识工程分析平台",
        epilog="示例: ontoderive init my-project --with-tools --derive --check",
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    # init
    p_init = sub.add_parser("init", help="初始化新项目")
    p_init.add_argument("name", help="项目名称")

    # derive
    p_derive = sub.add_parser("derive", help="正向推导")
    p_derive.add_argument("--project", default=".", help="项目路径")
    p_derive.add_argument("--with-tools", action="store_true", help="前置 ToolForge 匹配")
    p_derive.add_argument("--goal", help="目标描述")
    p_derive.add_argument("--tool-context", default="", help="ToolForge 上下文关键词")

    # check
    p_check = sub.add_parser("check", help="规约检查")
    p_check.add_argument("--project", default=".", help="项目路径")

    # rounds
    p_generate = sub.add_parser("generate", help="生成推导报告")
    p_generate.add_argument("--project", default=".", help="项目路径")
    p_generate.add_argument("--export", choices=["jsonld", "turtle"], help="导出为本体格式")
    p_rounds = sub.add_parser("rounds", help="多轮迭代")
    p_rounds.add_argument("--project", default=".", help="项目路径")
    p_rounds.add_argument("n", type=int, default=3, help="迭代轮数")

    # toolforge
    p_tf = sub.add_parser("toolforge", help="思维工具匹配")
    p_tf.add_argument("goal", help="目标描述")
    p_tf.add_argument("--context", default="", help="上下文关键词")
    p_tf.add_argument("--inference-guide", action="store_true", help="输出推导指导")
    p_tf.add_argument("--json", action="store_true", help="JSON输出")

    # formal (v3.2)
    p_formal = sub.add_parser("formal", help="形式化推理(Phase1-4管线)")
    p_formal.add_argument("--text", help="原始文本输入")
    p_formal.add_argument("--project", default=".", help="项目路径")
    # watch
    p_watch = sub.add_parser("watch", help="文件监听自动重推导")
    p_watch.add_argument("--project", default=".", help="项目路径")
    p_watch.add_argument("--interval", type=int, default=5, help="检测间隔(秒)")
    # extract
    p_extract = sub.add_parser("extract", help="从文本/URL提取事实")
    p_extract.add_argument("source", help="源文本或文件路径")
    p_extract.add_argument("--to", default="facts/data.md", help="输出路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 路由到对应功能
    if args.command == "init":
        from engine.core.derive import OntoDerive

        root = Path(args.name)
        for d in ["facts", "entities", "inferences", "protocols", "scheme", "_logs"]:
            (root / d).mkdir(parents=True, exist_ok=True)
        (root / "facts" / "data.md").write_text(
            "| 编号 | 数据 | 数值 | 来源 |\n|------|------|------|------|\n| D-F1 | 待填充 | — | — |\n"
        )
        (root / "facts" / "policy.md").write_text(
            "| 编号 | 政策 | 发布主体 | 日期 |\n|------|------|---------|------|\n| P-F1 | 待填充 | — | — |\n"
        )
        (root / "entities" / "actors.md").write_text(
            "| 实体 | 类型 | 角色 |\n|------|------|------|\n| ORG-待填充 | 组织 | — |\n"
        )
        (root / "inferences" / "analysis.md").write_text(
            "## INF-L1：待推导\n\n- derives_from: [D-F1]\n"
        )
        (root / "scheme" / "report.md").write_text("# 分析报告\n\n待补充。\n")
        (root / "README.md").write_text(
            f"# {args.name}\n\n> OntoDerive v3.5.0\n\n```bash\nontoderive derive --project .\nontoderive check --project .\n```\n"
        )
        print(f"✅ 项目 '{args.name}' 已初始化")

    elif args.command in ("derive", "check", "rounds", "generate"):
        from engine.core.derive import OntoDerive

        od = OntoDerive(args.project)

        # ToolForge 前置
        if getattr(args, "with_tools", False):
            from engine.toolforge import ToolForge

            tf = ToolForge()
            goal = getattr(args, "goal", "") or ""
            context = getattr(args, "tool_context", "") or ""
            print(f"\n{'━' * 50}")
            print("  🧰 ToolForge 前置匹配")
            print(f"     目标: {goal or '(未指定)'}")
            print(f"{'━' * 50}")
            guide = tf.to_inference_guide(goal, context)
            guide_path = Path(args.project) / "inferences" / "_toolforge_guide.md"
            guide_path.parent.mkdir(parents=True, exist_ok=True)
            guide_path.write_text(guide)
            top = tf.select(goal, context, top_n=3)
            if top:
                for t in top:
                    print(f"      {t['id']} {t['name']} (匹配度:{t['score']})")

        if args.command == "derive":
            od.derive()
        elif args.command == "check":
            od.check()
        elif args.command == "rounds":
            od.run_rounds(args.n)
        elif args.command == "generate":
            fmt = getattr(args, "export", None)
            if fmt:
                od.derive()  # 先推导再导出
                try:
                    from engine.formalize import Formalizer
                    from engine.foundation.ontology_map import OntologyMapper
                    fz = Formalizer()
                    all_text = ""
                    for d in ["facts", "entities", "inferences", "scheme"]:
                        for f in Path(args.project).glob(f"{d}/**/*.md"):
                            all_text += f.read_text() + "\n"
                    kb = fz.extract_from_text(all_text, mode="rule_only")
                    om = OntologyMapper()
                    output = om.export(kb, fmt=fmt)
                    out_path = Path(args.project) / f"export.{fmt if fmt != 'jsonld' else 'json'}"
                    out_path.write_text(output)
                    print(f"[export] ✅ {out_path} ({len(output)}字符)")
                except Exception as e:
                    print(f"[export] ❌ {e}")
            else:
                od.generate_report()

    elif args.command == "toolforge":
        from engine.toolforge import ToolForge

        tf = ToolForge()
        if args.inference_guide:
            print(tf.to_inference_guide(args.goal, args.context))
        elif args.json:
            import json

            print(
                json.dumps(
                    tf.select(args.goal, args.context, 5),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            tf.report(args.goal, args.context)

    elif args.command == "formal":
        from engine.core.derive import OntoDerive
        od = OntoDerive(args.project)
        text = getattr(args, "text", None)
        result = od.derive_formal(text=text)
        print(result.get("report", "推理完成")[:3000])

    elif args.command == "watch":
        from engine.watcher import FileWatcher
        w = FileWatcher(args.project)
        print(f"[watch] 监听中... 间隔{args.interval}秒, Ctrl+C停止")
        w.watch(interval=args.interval, auto_run=True)

    elif args.command == "extract":
        from engine.formalize import Formalizer
        fz = Formalizer()
        kb = fz.extract_from_text(args.source)
        md = fz.to_markdown(kb)
        output = Path(args.project) / args.to if args.project != "." else Path(args.to)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md)
        print(f"[extract] ✅ {len(kb.facts)}事实/{len(kb.entities)}实体 → {output}")


if __name__ == "__main__":
    main()
