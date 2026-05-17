## BOOT-01：文档声明与实现的一致性

推导过程：
1. README声明了4项核心能力(init/derive/check/rounds)(D-F10)
2. 引擎实际实现了6项(init/derive/check/resolve/rounds/generate)(D-F11)
3. 比较：文档声明 < 引擎实现，超出的2项(resolve/generate)是额外能力
4. 推论：文档声明完整但未覆盖全部实现——README更新后可提及resolve和generate
- derives_from: [D-F10, D-F11]
- confidence: high

## BOOT-02：框架文件完整性

推导过程：
1. CLAUDE.md声称框架有"4步标准操作流程"(FILE-CLAUDE)
2. 核心框架文件共6个(CLAUD/README/元模型/方案v2/引擎/命名空间)
3. 示例文件共8个(examples/z-park)
4. 自举验证文件共5个(self-verify/docs)
5. 推论：框架文件完整，目录结构清晰
- derives_from: [D-F1, D-F12]
- confidence: high

## BOOT-03：自举循环的可重复性

推导过程：
1. self-verify/docs项目已经提取了v2技术方案的30个事实
2. 引擎检查结果为7/8通过(Scheme: 7/8通过已于v2设计方案中的D-F27~D-F30自举验证数据吻合)
3. 全量验证(full)进一步提取了所有框架文件的元数据
4. 推论：自举循环可在任意框架版本上重复执行，验证版本间一致性
- derives_from: [D-F12, D-F8]
- confidence: high

## BOOT-04：元类型覆盖完备性

推导过程：
1. 元模型定义声称10元类型(D-F3)
2. 引擎实现了8条规约(ID后缀26种)(D-F4, D-F5)
3. PROBABILISTIC和METRIC两种元类型已在文档中定义但引擎中尚未实现对应规约
4. 推论：元类型覆盖=100%(10/10在文档中), 实现覆盖=80%(8/10在引擎中)
- derives_from: [D-F3, D-F4, D-F5]
- confidence: medium
