# OntoDerive Knowledge Namespace System (OD-NS)

> 版本 v1.0 | 2026-05-16
> 命名空间体系：确保知识标识在框架演进过程中保持唯一性、可追溯性、可迁移性。

---

## 一、设计原则

1. **全局唯一**：每个知识实体在整个框架历史中只有一个永久ID
2. **可版本化**：ID携带版本信息，支持跨版本引用
3. **领域隔离**：不同领域使用不同前缀，防止命名冲突
4. **人类可读**：ID结构对人类和AI同样可理解
5. **可废弃**：ID不删除，仅标记deprecated，保留历史引用

## 二、命名空间结构

```
od:{domain}:{type}-{name}@{version}
│  │        │         │
│  │        │         └── 版本(可省略，默认latest)
│  │        └── 实体类型+名称(如ORG-国转中心)
│  └── 领域(如guozhuan, z-park, meta)
└── OntoDerive根命名空间
```

## 三、核心领域

| 领域 | 用途 | 示例 |
|------|------|------|
| `meta` | 元模型概念 | `od:meta:type-PROBABILISTIC` |
| `proto` | 规约规则 | `od:proto:C-05` |
| `theory` | 理论引用 | `od:theory:bayes`, `od:theory:shannon` |
| `core` | 核心引擎 | `od:core:derive.py@1.2.0` |
| `user` | 用户项目 | 具体项目的命名空间 |

## 四、实体版本化

```text
od:guozhuan:INF-L1               → 初始版本(无后缀=首次定义)
od:guozhuan:INF-L1@v2            → 二次迭代版本
od:guozhuan:INF-L1@deprecated    → 已废弃(保留引用)
```

## 五、实施规则

1. 所有新实体必须使用 `od:{domain}:` 前缀
2. 版本号使用语义化版本(semver)
3. 废弃标记必须在 `_deprecated/` 目录中保留副本
4. 跨版本迁移记录在 `migrations/` 目录
