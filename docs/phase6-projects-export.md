# Phase 6 项目保存与多格式导出

## 范围

第六阶段实现本地项目持久化、YAML 版本快照与 YAML / JSON / Markdown 导出。该阶段不实现登录、多人协作、云同步、权限控制、Word/PDF 导出。

## 数据库

后端使用 SQLite，启动 `app.main` 时自动初始化：

```text
backend/data/novel2script.db
```

可通过 `NOVEL2SCRIPT_DB_PATH` 覆盖数据库位置。数据库包含两张表：

- `projects`：保存标题、类型、小说原文、章节 JSON、当前 YAML、校验结果和生成模式。
- `script_versions`：保存某个项目的 YAML 快照、校验结果、版本名和说明。

删除项目会级联删除版本。

## 后端接口

- `POST /api/projects`：创建项目。
- `GET /api/projects`：项目列表。
- `GET /api/projects/{project_id}`：项目详情。
- `PUT /api/projects/{project_id}`：更新项目。
- `DELETE /api/projects/{project_id}`：删除项目。
- `POST /api/projects/{project_id}/versions`：创建版本快照。
- `GET /api/projects/{project_id}/versions`：版本列表。
- `GET /api/projects/{project_id}/versions/{version_id}`：版本详情。
- `POST /api/projects/{project_id}/versions/{version_id}/restore`：恢复版本。
- `GET /api/projects/{project_id}/export/yaml`：导出 YAML。
- `GET /api/projects/{project_id}/export/json`：导出 JSON。
- `GET /api/projects/{project_id}/export/markdown`：导出 Markdown。

保存项目和版本时后端会重新调用 `validate_script_yaml`。无效 YAML 允许保存，但 JSON / Markdown 导出要求 YAML 能被解析。

## 前端使用

1. 输入小说并识别章节。
2. 生成或编辑 YAML。
3. 点击顶部“保存”，首次保存填写标题和类型。
4. 左侧项目列表可打开历史项目或删除项目。
5. YAML 区下方“版本历史”可保存快照并恢复。
6. 顶部导出入口支持 YAML、JSON、Markdown。

## 限制

- 无登录，所有项目为当前本地服务实例共享。
- 无云同步，迁移项目需要迁移 SQLite 文件。
- 无多人协作和冲突解决。
- Markdown 是基础阅读排版，不是最终出版格式。
- SQLite 适合本地和演示场景，高并发产品环境建议升级数据库。
