"""Reasoner utility functions"""

def _detect_domain(engine, self, value, label):
    """从值和标签中检测语义域, 优先用值的显式单位"""
    vs = str(value)
    for suffix, domain in self.VALUE_UNIT_MAP.items():
        if suffix in vs:
            return domain
    for domain, keywords in self.UNIT_GROUPS.items():
        if any(kw in label for kw in keywords):
            return domain
    return None

_STOP_CHARS = set("的是在与和及年第个月日一二三四五六七八九十前后")


def _char_overlap(engine, self, label_a, label_b):
    """检测两个标签的共同CJK字符数 ≥ 阈值"""
    chars_a = {c for c in label_a if "一" <= c <= "鿿" and c not in self._STOP_CHARS}
    chars_b = {c for c in label_b if "一" <= c <= "鿿" and c not in self._STOP_CHARS}
    return len(chars_a & chars_b) >= 2


def _comparable(engine, self, label_a, label_b, val_a=None, val_b=None):
    """判断两个事实是否可比较 — 域匹配+字符重叠"""
    if val_a is not None and val_b is not None:
        dom_a = self._detect_domain(val_a, label_a)
        dom_b = self._detect_domain(val_b, label_b)
        if dom_a and dom_b:
            if dom_a != dom_b:
                return False
            return self._char_overlap(label_a, label_b)
        if dom_a or dom_b:
            return False
    for group, keywords in self.UNIT_GROUPS.items():
        a_in = any(kw in label_a for kw in keywords)
        b_in = any(kw in label_b for kw in keywords)
        if a_in and b_in:
            return self._char_overlap(label_a, label_b)
    return False


def _extract_prefix(engine, self, id_str):
    """从ID中提取完整前缀模式 (如 D-F1→D-F, ORG-xxx→ORG-)"""
    # 按长度降序匹配, 优先匹配更长模式 (INF-V2- 优先于 INF-)
    for prefix in sorted(self._ID_PREFIX_MAP.keys(), key=lambda x: -len(x)):
        if id_str.startswith(prefix):
            return prefix
    # 回退: 首个分隔符前的部分
    return id_str.split("-")[0] if "-" in id_str else id_str[:3]


def _guess_parent(engine, self, prefix, type_map):
    """根据前缀模式猜测最可能的父类型 — 基于ID前缀→类型映射"""
    known = self._ID_PREFIX_MAP
    # 直接匹配: 如果前缀以已知前缀开头, 返回对应类型
    for kp, parent in sorted(known.items(), key=lambda x: -len(x[0])):
        if prefix.startswith(kp) or kp.startswith(prefix):
            return parent
    # 单字母/短前缀: 基于字符重叠找最相似的已知前缀
    best, best_score = "DOMAIN", 0
    for kp in known:
        score = len(set(prefix) & set(kp))
        if score > best_score:
            best_score = score
            best = known[kp]
    return best


def _closest_known(engine, self, prefix):
    """找到最相似的已知ID前缀"""
    best, best_score = "ORG-", 0
    for kp in self._ID_PREFIX_MAP:
        score = len(set(prefix) & set(kp))
        if score > best_score:
            best_score = score
            best = kp
    return best


def _project_profile(engine, self, project):
    """提取项目特征向量: [事实数, 推偶数, 平均引用数, 数值事实比, 政策事实比]"""
    facts = project.get("facts", {})
    infs = project.get("inferences", {})
    n_f = len(facts)
    n_i = len(infs)
    avg_df = sum(len(i.get("derives_from", [])) for i in infs.values()) / max(n_i, 1)
    num_ratio = sum(1 for f in facts.values() for v in [str(f.get("value", ""))] if re.search(r"\d", v)) / max(
        n_f, 1
    )
    pol_ratio = sum(1 for f in facts.values() if "政策" in str(f.get("desc", ""))) / max(n_f, 1)
    return [n_f / 20, n_i / 10, avg_df / 5, num_ratio, pol_ratio]


def _cosine_similarity(engine, self, a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = (sum(x * x for x in a) or 1) ** 0.5
    norm_b = (sum(x * x for x in b) or 1) ** 0.5
    return dot / (norm_a * norm_b)


