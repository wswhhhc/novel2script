# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Novel2Script 是 AI 小说转剧本工具，支持章节识别、AI 多阶段剧本生成、YAML Schema 校验、Monaco 编辑器、SQLite 项目管理和多格式导出。

**核心特性**：默认 Mock 模式不调用真实 AI，适合演示；AI 模式需显式配置 `ENABLE_AI_GENERATION=true`。

## 常用命令

### 启动服务

```bash
# Windows
scripts/start-dev.ps1

# macOS/Linux
bash scripts/start-dev.sh

# 手动启动后端（在项目根目录）
python -m uvicorn app.main:app --reload --app-dir backend --host 127.0.0.1 --port 8000

# 手动启动前端
cd frontend
npm install
npm run dev
```

访问地址：
- 前端：http://127.0.0.1:5173
- 后端：http://127.0.0.1:8000/health

### 测试

```bash
# 后端测试（在项目根目录）
python -m pytest backend/tests

# 前端构建验证
cd frontend
npm run build

# 前端静态 smoke test
cd frontend
npm run smoke

# 端到端 smoke test（需先启动服务）
# Windows
scripts/smoke-test.ps1
# macOS/Linux
bash scripts/smoke-test.sh
```

### Docker

```bash
cp .env.example .env
docker compose --project-name novel2script up --build
```

## 技术架构

### 后端结构（FastAPI）

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口，CORS 配置
│   ├── config/
│   │   └── settings.py      # 环境变量、路径、AI 配置
│   ├── routers/             # API 路由层
│   │   ├── chapters.py      # POST /api/parse-chapters
│   │   ├── script.py        # POST /api/generate-script, /api/validate-yaml
│   │   └── projects.py      # 项目 CRUD、版本管理、导出
│   ├── services/            # 业务逻辑层
│   │   ├── chapter_parser.py       # 章节标题识别（正则模式匹配）
│   │   ├── script_generator.py     # AI 5 阶段生成 + Mock 模式
│   │   ├── script_validator.py     # YAML Schema 校验
│   │   ├── ai_client.py            # OpenAI 兼容 API 调用
│   │   ├── prompt_loader.py        # Prompt 模板加载
│   │   ├── project_service.py      # SQLite 项目、版本管理
│   │   └── export_service.py       # YAML/JSON/Markdown 导出
│   ├── schemas/             # Pydantic 数据模型
│   └── db/
│       └── database.py      # SQLite 初始化、表定义
└── tests/
    ├── test_chapter_parser.py
    └── test_script_validator.py
```

### 前端结构（React + TypeScript）

```
frontend/src/
├── App.tsx                  # 主应用状态、工作流编排
├── main.tsx                 # React 入口
├── api/
│   ├── client.ts            # 后端 API 调用函数
│   └── types.ts             # TypeScript 接口定义
├── components/              # React 组件
│   ├── NovelInput.tsx       # 小说输入、文件上传
│   ├── ChapterList.tsx      # 章节识别结果展示
│   ├── GenerationPanel.tsx  # 识别/生成控制按钮
│   ├── YamlEditor.tsx       # Monaco Editor YAML 编辑
│   ├── ValidationPanel.tsx  # Schema 错误展示
│   ├── ProjectSidebar.tsx   # 项目列表
│   ├── VersionHistory.tsx   # 版本快照、恢复
│   ├── ExportPanel.tsx      # YAML/JSON/Markdown 导出
│   └── SaveProjectDialog.tsx
└── utils/
    ├── yaml.ts              # js-yaml 包装
    └── download.ts          # 浏览器下载工具
```

## AI 生成流程（5 阶段）

**入口**：`backend/app/services/script_generator.py`

### Mock 模式（默认）
- 返回 `examples/script-output-1.yaml`
- 不调用 AI，不发送用户数据
- 环境变量：`ENABLE_AI_GENERATION=false`

### AI 模式（5 阶段）

需配置环境变量：
```env
ENABLE_AI_GENERATION=true
MODEL_PROVIDER=openai
MODEL_NAME=your-model-name
MODEL_API_KEY=your-api-key
MODEL_BASE_URL=https://api.openai.com/v1
```

生成流程：
1. **章节分析**（`01_chapter_analysis.txt`）→ JSON 结构化摘要、人物、事件
2. **角色提取**（`02_character_extraction.txt`）→ 统一角色表
3. **场景规划**（`03_scene_planning.txt`）→ 场景拆分大纲
4. **剧本生成**（`04_script_generation.txt`）→ 完整 YAML 剧本
5. **YAML 修复**（`05_yaml_fix.txt`）→ 若 Schema 校验失败，自动修复（最多 3 次）

Prompt 模板位于 `prompts/` 目录，使用 `{title}`, `{genre}`, `{chapters}` 等占位符。

## YAML Schema

**路径**：`schemas/script.schema.json`

**顶层结构**：
```yaml
script:
  title: string
  genre: string
  version: "1.0.0"
  source:
    chapter_count: int (3-20)
    chapters: [{id: "C001", title: string, word_count: int}]
  characters: [{id: "CHAR001", name, role, first_appearance: "C001", ...}]
  scenes: [{id: "S001", title, source_chapters: ["C001"], location, time, characters: ["CHAR001"], purpose, beats: []}]
  adaptation_notes: [{type: deletion|merge|transformation|addition, description, reason}]
  open_questions: [{question, context?}]
```

**关键约束**：
- 章节 ID：`C001-C999`
- 角色 ID：`CHAR001-CHAR999`
- 场景 ID：`S001-S999`
- Beat 类型：`action`, `dialogue`, `narration`, `transition`, `note`
- `dialogue` beat 必须有 `character` 字段

校验实现：`backend/app/services/script_validator.py`（jsonschema）

## 配置与限制

**后端限制**（`backend/app/config/settings.py`）：
- `min_chapters = 3`：最少章节数
- `max_chapters = 20`：最多章节数
- `max_input_length = 50000`：输入总字数上限
- `max_chapter_length = 10000`：单章节字数警告阈值
- AI Prompt 章节裁剪：单章超过 8000 字时取首尾各 4000 字

**前端环境变量**（`.env` 或 `vite.config.ts`）：
- `VITE_API_BASE_URL`：后端 API 地址，默认 `http://127.0.0.1:8000`

## 数据持久化

**SQLite 数据库**：`backend/data/novel2script.db`（自动创建）

**表结构**：
- `projects`：项目元数据（title, genre, source_content, current_yaml, validation, generation_mode）
- `script_versions`：版本快照（project_id, version_name, yaml, validation, note）

**Docker 持久化**：通过 `novel2script-data` volume 映射到容器 `/app/backend/data`。

## 章节识别

**实现**：`backend/app/services/chapter_parser.py`

支持格式（正则匹配）：
- `第一章 标题` / `第1章 标题`
- `Chapter 1: Title` / `Chapter One: Title`
- `1. 标题` / `01. 标题`
- `【1】标题` / `（1）标题`

识别逻辑：
1. 按行扫描匹配章节标题正则
2. 提取标题和内容（下一章节前的所有文本）
3. 计算字数（`len(content)`）
4. 生成章节 ID（`C001`, `C002`, ...）
5. 返回识别结果 + 警告（超长章节、输入过长、章节不足）

## 导出格式

**实现**：`backend/app/services/export_service.py`

- **YAML**：当前项目 YAML 文本
- **JSON**：解析 YAML 后的 JSON 结构
- **Markdown**：人类可读格式（标题、角色表、场景列表、对白展开）

导出要求：
- 必须先保存项目（需要 `project.id`）
- JSON/Markdown 导出要求 YAML 可解析（`yaml.safe_load` 成功）

## 示例数据

**小说示例**（`examples/`）：
- `novel-sample-1.txt`：都市 3 章（推荐演示）
- `novel-sample-2.txt`：悬疑 5 章
- `novel-sample-3.txt`：古装武侠 4 章
- `novel-edge-too-few-chapters.txt`：章节不足边界测试
- `novel-edge-mixed-chapter-formats.txt`：混合格式测试

**剧本示例**：
- `script-output-1.yaml`：Mock 模式标准输出
- `invalid-script-*.yaml`：Schema 校验失败 fixture

## 开发注意事项

### 修改 YAML Schema
1. 更新 `schemas/script.schema.json`
2. 更新 `examples/script-output-1.yaml` 确保符合新 Schema
3. 运行 `python -m pytest backend/tests/test_script_validator.py` 验证
4. 更新相关 Prompt 模板（`prompts/04_script_generation.txt`）

### 修改 AI Prompt
1. 编辑 `prompts/` 目录下的 `.txt` 文件
2. 占位符格式：`{variable_name}`（由 `prompt_loader.py` 替换）
3. 测试 AI 模式：设置 `ENABLE_AI_GENERATION=true` 并配置真实 API Key
4. 如修改阶段间传递的 JSON 结构，同步更新 `script_generator.py` 中的解析逻辑

### 添加新 API 路由
1. 在 `backend/app/routers/` 创建或编辑路由文件
2. 在 `backend/app/main.py` 中 `app.include_router(your_router)`
3. 在 `frontend/src/api/client.ts` 添加对应调用函数
4. 在 `frontend/src/api/types.ts` 定义 TypeScript 接口
5. 在前端组件中调用新 API

### 前端状态管理
所有应用状态在 `App.tsx` 中管理（无 Redux/Zustand），通过 props 传递给子组件。核心状态：
- `currentProject`：当前打开项目
- `yamlText`：YAML 编辑器内容
- `validation`：Schema 校验结果
- `dirty`：是否有未保存修改

### CORS 配置
后端 `main.py` 中硬编码允许 `http://127.0.0.1:5173` 和 `http://localhost:5173`。如更改前端端口，需同步更新 `allow_origins`。
