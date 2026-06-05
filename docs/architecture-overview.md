# Novel2Script 架构概览

## 总体结构

```text
React 工作台
  -> FastAPI API
    -> 章节解析服务
    -> 剧本生成服务
      -> Mock 输出
      -> AI 客户端
      -> Prompt 模板
    -> YAML 校验服务
      -> JSON Schema
      -> 业务引用校验
    -> 项目服务
      -> SQLite
      -> 导出服务
```

## 后端模块

- `backend/app/main.py`：应用入口、CORS、路由注册和健康检查。
- `backend/app/routers/chapters.py`：章节解析接口。
- `backend/app/routers/script.py`：生成模式、YAML 校验、剧本生成接口。
- `backend/app/routers/projects.py`：项目、版本和导出接口。
- `backend/app/services/chapter_parser.py`：章节识别和输入校验。
- `backend/app/services/script_generator.py`：Mock / AI 生成编排。
- `backend/app/services/script_validator.py`：YAML Schema 和业务规则校验。
- `backend/app/services/project_service.py`：SQLite 项目和版本管理。
- `backend/app/services/export_service.py`：YAML / JSON / Markdown 导出。

## 前端模块

- `frontend/src/App.tsx`：工作台状态和主流程编排。
- `frontend/src/api/client.ts`：后端 API 客户端。
- `frontend/src/components/NovelInput.tsx`：小说输入。
- `frontend/src/components/ChapterList.tsx`：章节列表。
- `frontend/src/components/GenerationPanel.tsx`：生成控制和模式展示。
- `frontend/src/components/YamlEditor.tsx`：YAML 编辑器。
- `frontend/src/components/ProjectSidebar.tsx`：项目列表。
- `frontend/src/components/VersionHistory.tsx`：版本历史。
- `frontend/src/components/ExportPanel.tsx`：导出入口。

## 数据与配置

- YAML Schema：`schemas/script.schema.json`
- Prompt 模板：`prompts/`
- 示例输入输出：`examples/`
- SQLite 默认路径：`backend/data/novel2script.db`
- 环境变量模板：`.env.example`

## 设计取舍

- 默认 Mock 模式，保证评审环境无需 Key 也能完整演示。
- AI 模式只通过环境变量启用，避免误调用和密钥泄漏。
- SQLite 满足本地作品提交和单机演示，不引入复杂云依赖。
- 输出采用结构化 YAML，便于校验、编辑、版本管理和格式转换。
