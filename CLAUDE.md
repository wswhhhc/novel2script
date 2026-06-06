# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Novel2Script — AI 驱动的小说转剧本系统。FastAPI + React + SQLite，五阶段 AI 生成链路 + 332 行 JSON Schema 校验。

**技术栈**：FastAPI / SQLite / React 18 / TypeScript / Vite / Monaco Editor / Tailwind CSS

## 常用命令

```bash
# ----- 后端 -----
# 启动（项目根目录）
python -m uvicorn app.main:app --reload --app-dir backend --host 127.0.0.1 --port 8000

# 测试
python -m pytest backend/tests -v              # 全部
python -m pytest backend/tests/test_chapter_parser.py -v  # 单个

# ----- 前端 -----
cd frontend
npm install                                      # 首次
npm run dev                                      # 开发
npm run build                                    # 构建验证
npm run smoke                                    # 静态 smoke test
npx vitest run                                   # 组件测试
npx vitest --reporter verbose src/components/__tests__/NovelInput.test.tsx  # 单个

# ----- Docker -----
docker compose --project-name novel2script up --build
```

## 架构

### 后端（`backend/app/`）

```
routers/        # API 路由
├── chapters.py    POST /api/parse-chapters
├── script.py      POST /api/script/generate, /api/script/generate/stream, /api/script/validate, GET /api/script/mode
├── projects.py    CRUD + 版本管理 + 导出（YAML/JSON/Markdown/PDF）
└── batch.py       批量删除/校验/统计

services/       # 业务逻辑
├── chapter_parser.py     正则匹配 8+ 种章节格式
├── script_generator.py   Mock / AI 五阶段生成 + 流式生成
├── script_validator.py   jsonschema 校验 + 业务规则
├── ai_client.py          OpenAI + Anthropic 双 provider，含重试/重试判定
├── generation_cache.py   按 stage+prompt 缓存中间结果
├── prompt_loader.py      {variable} 模板替换 + 章节裁剪
├── project_service.py    SQLite CRUD + 版本快照恢复
├── export_service.py     YAML/JSON/Markdown 导出
└── pdf_export_service.py reportlab PDF 生成

config/settings.py   环境变量、路径、AI 配置、章节限制
schemas/              Pydantic 请求/响应模型
db/database.py        SQLite 表定义（projects + script_versions）
```

### 前端（`frontend/src/`）

```
App.tsx              所有状态在顶层管理（无 Redux），通过 props 下发
api/client.ts        API 调用（含流式 SSE）
api/types.ts         TypeScript 接口定义
components/          每个功能一个组件，含 __tests__/ 目录
utils/               yaml.ts（js-yaml 封装）、download.ts
```

**核心状态**：`currentProject`, `yamlText`, `validation`, `dirty` — 均在 `App.tsx` 管理。

## AI 生成流程

入口：`backend/app/services/script_generator.py`

### 模式切换
| 变量 | 效果 |
|------|------|
| `ENABLE_AI_GENERATION=false`（默认） | Mock：返回 `examples/script-output-1.yaml` | |
| `ENABLE_AI_GENERATION=true` | AI：五阶段调用大模型 |

### AI 五阶段
```
章节分析 → 角色提取 → 场景规划 → 剧本生成 → Schema 校验 → 失败则自动修复（最多 3 次）
```
- 每阶段输出 JSON 传递到下一阶段
- Prompt 模板在 `prompts/`，占位符 `{title}`, `{genre}`, `{chapters}`
- 单章 >8000 字自动裁剪取首尾各 4000 字
- `script_generator.py` 中有 `MockScriptGenerator` / `AIScriptGenerator` / `BaseGenerator` 类体系

### 流式生成
`POST /api/script/generate/stream` 返回 NDJSON 事件：`status`, `yaml_delta`, `validation`, `done`

### AI 客户端（`ai_client.py`）
- 支持 OpenAI API 兼容（DeepSeek / GPT）和 Anthropic Claude
- 自动重试（可配置次数），失败回退
- 流式调用：`_stream_openai()` / `_stream_anthropic()`
- JSON 输出解析：`parse_json_response()` 含错误恢复和代码块提取

## YAML Schema（`schemas/script.schema.json`）

```yaml
script:
  title, genre, version: "1.0.0"
  source: { chapter_count, chapters: [{id: C001, title, word_count}] }
  characters: [{id: CHAR001, name, role, first_appearance: C001, ...}]
  scenes: [{id: S001, title, source_chapters: [C001], location, time, characters: [CHAR001], beats: []}]
  adaptation_notes: [{type: deletion|merge|transformation|addition, ...}]
  open_questions: [{question, context?}]
```
- ID 约束：C001-C999 / CHAR001-CHAR999 / S001-S999
- beat 类型：action, dialogue, narration, transition, note
- dialogue 必须有 character 字段

## DB

SQLite `backend/data/novel2script.db`（自动创建）：
- `projects`：title, genre, source_content, current_yaml, validation, generation_mode
- `script_versions`：project_id, version_name, yaml, validation, note（快照）

## 关键配置（`backend/app/config/settings.py`）

| 参数 | 默认 | 说明 |
|------|------|------|
| min_chapters | 3 | 最少章节 |
| max_chapters | 20 | 最多章节 |
| max_input_length | 50,000 | 总字数上限 |
| max_chapter_length | 10,000 | 单章警告阈值 |
| model_provider | openai | 支持 openai / anthropic |
| model_max_retries | 2 | AI 调用重试次数 |
| auto_fix_attempts | 3 | YAML 修复最大迭代 |

## 数据流

1. 用户上传小说 → `chapter_parser.py` 识别章节
2. 触发生成 → `script_generator.py` 执行 5 阶段（Mock 直接返回示例；AI 调用 ai_client）
3. `script_validator.py` 校验 YAML → 失败则 stage 5 自动修复
4. 用户编辑 → `project_service.py` 保存项目 / 创建版本快照
5. 导出：YAML/JSON/Markdown `export_service.py` / PDF `pdf_export_service.py`

## 修改指南

- **YAML Schema**：更新 `schemas/script.schema.json` → 更新 `examples/script-output-1.yaml` → `pytest test_script_validator.py` → 同步 `prompts/04_script_generation.txt`
- **AI Prompt**：编辑 `prompts/*.txt`（占位符 `{variable}`）→ 如改阶段间 JSON 结构，同步 `script_generator.py`
- **新 API 路由**：`routers/` 建文件 → `main.py` 中 `app.include_router()` → `api/client.ts` 加函数 → `api/types.ts` 加类型
- **前端组件**：`components/` 加文件 → `App.tsx` 挂状态 → props 传递（无全局状态库）
- **CORS**：`main.py` 硬编码 `allow_origins`，改端口需同步更新

## 部署

- **Nginx 反代**：需 `--root-path /prefix` 启动 uvicorn（`--root-path /novel2-api`），否则 Swagger UI 404
- **Mock/AI 切换**：`.env` 中 `ENABLE_AI_GENERATION=true/false`
- **Docker**：`docker compose --project-name novel2script up --build`（SQLite volume 持久化）

## 示例数据

`examples/`：
- `novel-sample-1.txt`：都市 3 章 **推荐演示**
- `novel-sample-2.txt`：悬疑 5 章
- `novel-sample-3.txt`：古装武侠 4 章
- `novel-edge-*.txt`：边界测试（章节不足 / 混合格式）
- `script-output-1.yaml`：Mock 标准输出
- `invalid-script-*.yaml`：校验失败 fixture
