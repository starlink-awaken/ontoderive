"""
Formalizer — 符号化引擎 (Phase 1+2)
=====================================
LLM从自然语言提取结构化知识 → 本体对齐 → OntoLang符号化
"""
import json, re
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SymbolicFact:
    id: str
    description: str
    value: str
    source: str = ""
    confidence: float = 0.90
    category: str = "data"  # data | policy
    meta_type: str = "FACT"

@dataclass
class SymbolicEntity:
    id: str
    name: str
    entity_type: str  # ORG | ROL | PRJ
    role: str = ""
    meta_type: str = "DOMAIN"

@dataclass
class SymbolicInference:
    id: str
    title: str
    derives_from: List[str] = field(default_factory=list)
    conclusion: str = ""
    confidence: str = "inference"
    meta_type: str = "INFERENCE"

@dataclass
class FormalKnowledge:
    facts: List[SymbolicFact] = field(default_factory=list)
    entities: List[SymbolicEntity] = field(default_factory=list)
    inferences: List[SymbolicInference] = field(default_factory=list)
    abox: Dict = field(default_factory=dict)   # 断言箱: 具体实例
    tbox: Dict = field(default_factory=dict)   # 术语箱: 类型层级


class Formalizer:
    """LLM提取 + 规则降级 + 符号化"""

    def _rule_extract(self, text: str) -> FormalKnowledge:
        """规则引擎降级提取 — 零LLM, 正则匹配数值和实体"""
        knowledge = FormalKnowledge()
        fid_counter = 1
        # 提取数值事实
        patterns = [
            (r'(\d+)\s*家\s*(入驻)?企[业商]', '入驻企业数', '家'),
            (r'(\d+)\s*次.*?(对接|交易|调用)', '对接量', '次'),
            (r'(\d+\.?\d*)\s*%\s*(转化|成功|覆盖|增长|满意)', '比率', '%'),
            (r'与\s*(\d+)\s*所\s*(高校|大学|机构)', '合作高校', '所'),
            (r'(\d+)\s*[人名位个].*?(经理|专家|博士|导师)', '人员数', '人'),
            (r'NPS.*?(\d+)', 'NPS得分', '分'),
            (r'(\d+\.?\d*)\s*[万亿千百]\s*(元|美元|营收|收入|预算|成本)', '金额', ''),
            (r'(\d+)\s*[台次个].*?(服务器|设备|机器)', '设备数', '台'),
        ]
        for pattern, desc, unit in patterns:
            for m in re.finditer(pattern, text):
                val = f"{m.group(1)}{unit}"
                knowledge.facts.append(SymbolicFact(
                    id=f"D-F{fid_counter}", description=desc, value=val,
                    source="规则提取", confidence=0.85,
                ))
                fid_counter += 1

        # 提取实体
        eid_counter = 1
        entity_patterns = [
            (r'([一-鿿]{2,4}(?:科技)?园区)', 'ORG', '运营主体'),
            (r'([一-鿿]{2,4}(?:平台|系统))', 'PRJ', '核心项目'),
            (r'([一-鿿]{2,4}(?:高校|大学|学院))', 'ORG', '合作方'),
            (r'([一-鿿]{2,4}(?:公司|集团))', 'ORG', '企业'),
        ]
        for pattern, etype, role in entity_patterns:
            for m in re.finditer(pattern, text):
                name = m.group(1)
                knowledge.entities.append(SymbolicEntity(
                    id=f"{'ORG' if etype=='ORG' else 'PRJ'}-{name}",
                    name=name, entity_type=etype, role=role,
                ))
                eid_counter += 1

        return knowledge

    EXTRACT_PROMPT = """你是知识工程提取专家。从以下文本中提取结构化知识。输出JSON。

文本:
{text}

提取规则:
1. facts: 找出具体的数据事实。每条包含id(D-F1~D-Fn), description(20字内), value(含单位), source(出处)
2. entities: 找出关键组织和角色。每条包含id(ORG-/ROL-/PRJ-), name(实体名), type(组织/角色/项目), role(职能)
3. inferences: 找出文中的推论/结论/判断。每条包含id(INF-L1~), title, derives_from(引用的事实id), conclusion

输出格式(只输出JSON):
{{"facts":[{{"id":"D-F1","description":"入驻企业","value":"240家","source":"第三章"}}],"entities":[{{"id":"ORG-国转中心","name":"国家技术转移中心","type":"组织","role":"运营主体"}}],"inferences":[{{"id":"INF-L1","title":"数字化是必然趋势","derives_from":["D-F1"],"conclusion":"需要建设平台"}}]}}"""

    def __init__(self, enhancer=None):
        self.enhancer = enhancer

    def extract_from_text(self, text: str, mode="llm_first") -> FormalKnowledge:
        """Phase 1: LLM主提取 → 降级规则引擎

        mode: llm_first (默认, LLM优先+规则降级)
              llm_only (仅LLM, 无降级)
              rule_only (仅规则, 零LLM)
        """
        knowledge = FormalKnowledge()

        # LLM主提取
        if mode != "rule_only" and self.enhancer and self.enhancer.available:
            print(f"[formalize] 🤖 LLM提取中 ({self.enhancer.model})...")
            # 分块处理长文本
            chunks = [text[i:i+2500] for i in range(0, min(len(text), 8000), 2500)]
            for chunk in chunks:
                result = self.enhancer._call(
                    self.EXTRACT_PROMPT.format(text=chunk),
                    "你是知识提取专家。只输出JSON。", 0.2
                )
                if result:
                    try:
                        data = json.loads(result)
                    except json.JSONDecodeError:
                        m = re.search(r'\{[\s\S]*\}', result)
                        data = json.loads(m.group()) if m else {}

                for f in data.get("facts", []):
                    knowledge.facts.append(SymbolicFact(
                        id=f.get("id", f"D-F{len(knowledge.facts)+1}"),
                        description=f.get("description", ""),
                        value=str(f.get("value", "")),
                        source=f.get("source", "LLM提取"),
                        confidence=0.90,
                    ))

                for e in data.get("entities", []):
                    knowledge.entities.append(SymbolicEntity(
                        id=e.get("id", f"ORG-{e.get('name','未知')[:10]}"),
                        name=e.get("name", ""),
                        entity_type=e.get("type", "组织"),
                        role=e.get("role", ""),
                    ))

                for inf in data.get("inferences", []):
                    knowledge.inferences.append(SymbolicInference(
                        id=inf.get("id", f"INF-L{len(knowledge.inferences)+1}"),
                        title=inf.get("title", ""),
                        derives_from=inf.get("derives_from", []),
                        conclusion=inf.get("conclusion", ""),
                    ))

        # LLM失败/超时 → 规则引擎降级 (仅llm_first模式)
        if not knowledge.facts:
            if mode == "llm_only":
                print("[formalize] ⚠️ LLM提取为空, llm_only模式不降级, 返回空结果")
            else:
                print("[formalize] ⚠️ LLM提取为空/超时, 已降级为规则引擎 (覆盖约15-20%)")
                knowledge = self._rule_extract(text)

        self._validate(knowledge)
        # 构建ABox/TBox
        self._build_abox_tbox(knowledge)
        return knowledge

    def _validate(self, knowledge: FormalKnowledge):
        """规则校验: TypeValidator检查ID格式"""
        try:
            from .typesystem import TypeValidator
        except ImportError:
            from typesystem import TypeValidator
        tv = TypeValidator()
        for f in knowledge.facts:
            if not tv.check_id(f.id).is_valid:
                f.id = f"D-F{hash(f.description) % 10000}"  # 自动修复
        for e in knowledge.entities:
            if not tv.check_id(e.id).is_valid:
                e.id = f"ORG-{e.name[:10]}"

    def _build_abox_tbox(self, knowledge: FormalKnowledge):
        """Phase 2: 构建ABox(断言)和TBox(术语)"""
        knowledge.abox = {
            "facts": {f.id: {"description": f.description, "value": f.value} for f in knowledge.facts},
            "entities": {e.id: {"name": e.name, "type": e.entity_type} for e in knowledge.entities},
        }
        knowledge.tbox = {
            "DOMAIN": {"subtypes": ["ORG", "ROL", "PRJ"]},
            "FACT": {"subtypes": ["DAT", "POL"]},
            "INFERENCE": {"subtypes": ["CLAIM", "STRATEGY", "DIAGNOSIS"]},
            "PROPERTY": {"numeric": ["value", "count", "rate"], "textual": ["description", "source"]},
        }

    def to_markdown(self, knowledge: FormalKnowledge) -> str:
        """符号化知识→Markdown (供现有derive/check消费)"""
        lines = ["# 形式化知识库\n"]
        if knowledge.facts:
            lines.append("## 事实\n")
            lines.append("| 编号 | 数据 | 数值 | 来源 |")
            lines.append("|------|------|------|------|")
            for f in knowledge.facts:
                lines.append(f"| {f.id} | {f.description} | {f.value} | {f.source} |")
            lines.append("")
        if knowledge.entities:
            lines.append("## 实体\n")
            lines.append("| 实体 | 类型 | 角色 |")
            lines.append("|------|------|------|")
            for e in knowledge.entities:
                lines.append(f"| **{e.id}** | {e.entity_type} | {e.role} |")
            lines.append("")
        if knowledge.inferences:
            lines.append("## 推论\n")
            for inf in knowledge.inferences:
                lines.append(f"### {inf.id}：{inf.title}")
                lines.append(f"- derives_from: {inf.derives_from}")
                if inf.conclusion:
                    lines.append(f"- 结论: {inf.conclusion}")
                lines.append(f"confidence: {inf.confidence}")
                lines.append("")
        return "\n".join(lines)
