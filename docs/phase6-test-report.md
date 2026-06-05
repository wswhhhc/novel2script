# Phase 6 测试报告

## 后端

运行命令：

```bash
cd backend
python -m pytest
```

结果：55 项通过。

新增覆盖：

- 创建项目成功。
- 项目列表返回已创建项目。
- 项目详情包含 YAML 和章节。
- 更新项目成功。
- 删除项目后详情返回 404。
- 创建版本成功。
- 版本列表返回版本。
- 版本详情包含完整 YAML。
- 恢复版本后 `current_yaml` 更新。
- 导出 YAML 返回原始 YAML。
- 导出 JSON 返回可解析 JSON。
- 导出 Markdown 包含标题、角色和场景。
- 无效项目 ID 返回 404。
- 无效 YAML 导出 JSON 返回明确错误。

## 前端

运行命令：

```bash
cd frontend
npm run smoke
npm run build
```

结果：

- `npm run smoke` 通过。
- `npm run build` 通过。

前端 smoke 覆盖：

- 保存项目入口存在。
- 项目列表入口存在。
- 版本历史入口存在。
- YAML / JSON / Markdown 导出入口存在。
- 原有生成、校验、复制、下载静态保护点仍存在。

## 已知限制

- 未引入端到端浏览器自动化测试。
- 版本对比未实现。
- Markdown 导出为基础排版。
- 本地 SQLite 数据不做用户隔离。
