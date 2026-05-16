# Contributing to OntoDerive

感谢你考虑为 OntoDerive 贡献代码！

## 开发流程

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feat/your-feature`
3. 提交变更: `git commit -m "feat: add xxx"`
4. 推送到分支: `git push origin feat/your-feature`
5. 创建 Pull Request

## 提交规范

使用 Conventional Commits 格式：

```
feat: 新功能
fix: Bug修复
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
python3 engine/derive.py --project examples/z-park --derive --check

# 自举验证
python3 engine/derive.py --project self-verify/docs --derive --check
```

## 命名空间规范

新增实体必须遵循 `od:{domain}:{type}-{name}` 格式。
详见 `ns/NAMESPACE.md`。
