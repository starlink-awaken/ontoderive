# 贝叶斯层演示示例——智能层的信念传播验证

> 本示例展示v2.1贝叶斯层的能力：置信度从离散标签升级为连续概率，
> 事实更新时信念自动沿derives_from链传播。

---

## 场景

某科技园区成果转化分析：
- D-F1: 入驻企业240家 → 置信度0.95(事实)
- D-F2: 年对接量80次 → 置信度0.95(事实)
- D-F3: 转化成功率8% → 置信度0.95(事实)
- INF-L1: 匹配效率不足(derives_from D-F1,D-F2,D-F3) → 传播后置信度 = avg(0.95,0.95,0.95) * 0.9 = 0.855

## 验证

```bash
# 信念传播
python3 -c "from engine.bayesian import BayesianLayer; bl=BayesianLayer('.'); bl.confidence_report()"

# 完整引擎检查(含C-09)
python3 engine/derive.py --project . --check
```
