# Novel2Script Backend

Novel2Script 后端服务，基于 FastAPI 实现章节解析、YAML 剧本校验和 AI 剧本生成。

## 功能

- `GET /health`：健康检查。
- `POST /api/chapters/parse`：解析小说章节，支持常见中文和英文章节标题格式。
- `POST /api/script/validate`：使用 `schemas/script.schema.json` 校验 YAML，并执行章节、角色、场景引用等业务校验。
- `POST /api/script/generate`：剧本生成，支持 Mock 模式和 AI 模式。
- `GET/POST/PUT/DELETE /api/projects`：本地项目管理。
- `POST/GET /api/projects/{project_id}/versions`：YAML 版本快照和历史。
- `GET /api/projects/{project_id}/export/{yaml|json|markdown}`：导出当前剧本。

## 安装依赖

在项目根目录执行：

```bash
pip install -r backend/requirements.txt
```

`openai` 已包含在默认依赖中。Anthropic Claude 是可选扩展：

```bash
pip install anthropic
```

## 启动服务

### Mock 模式（默认）

不调用真实 AI，返回示例 YAML，用于前后端联调：

```bash
uvicorn app.main:app --reload --app-dir backend
```

### AI 模式

调用真实 AI 生成剧本，需要配置环境变量：

```bash
# Windows
set ENABLE_AI_GENERATION=true
set MODEL_PROVIDER=openai
set MODEL_NAME=your-model-name
set MODEL_API_KEY=your-api-key-here
uvicorn app.main:app --reload --app-dir backend

# Linux/Mac
export ENABLE_AI_GENERATION=true
export MODEL_PROVIDER=openai
export MODEL_NAME=your-model-name
export MODEL_API_KEY=your-api-key-here
uvicorn app.main:app --reload --app-dir backend
```

启动后访问：

```text
http://127.0.0.1:8000/health
```

## SQLite 数据库

后端启动时会自动创建数据库和表，无需手动迁移：

```text
backend/data/novel2script.db
```

可通过环境变量覆盖位置：

```bash
set NOVEL2SCRIPT_DB_PATH=D:\data\novel2script.db
```

数据库仅用于本地项目、当前 YAML 和版本快照保存，不包含登录、权限或云同步能力。

## 环境变量配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `ENABLE_AI_GENERATION` | `false` | 是否启用 AI 生成（true/false） |
| `MODEL_PROVIDER` | `openai` | AI 提供商（openai/anthropic） |
| `MODEL_NAME` | `""` | 模型名称，AI 模式必填 |
| `MODEL_API_KEY` | `""` | API 密钥（必填） |
| `MODEL_BASE_URL` | `https://api.openai.com/v1` | API 基础地址 |
| `MODEL_TEMPERATURE` | `0.7` | 温度参数 |
| `MODEL_MAX_TOKENS` | `4000` | 最大输出 token 数 |
| `MODEL_TIMEOUT` | `120` | 超时时间（秒） |
| `MODEL_MAX_RETRIES` | `2` | 模型调用失败后的最大重试次数 |
| `AUTO_FIX_ATTEMPTS` | `3` | YAML 校验失败后的最大自动修复次数 |
| `NOVEL2SCRIPT_DB_PATH` | `backend/data/novel2script.db` | SQLite 数据库文件位置 |

## AI 生成流程

当启用 AI 生成时，系统会执行 5 阶段生成流程：

1. **章节分析**（`prompts/01_chapter_analysis.txt`）
   - 提取摘要、人物、事件、地点、时间线索、冲突等

2. **角色提取**（`prompts/02_character_extraction.txt`）
   - 生成统一角色表
   - 合并同一角色的不同称呼
   - 整理角色关系

3. **场景规划**（`prompts/03_scene_planning.txt`）
   - 将章节拆分为剧本场景
   - 定义场景地点、时间、出场角色、目的

4. **剧本生成**（`prompts/04_script_generation.txt`）
   - 生成完整 YAML 剧本
   - 包含动作、对白、旁白、转场

5. **校验与修复**（`prompts/05_yaml_fix.txt`）
   - 使用 Schema 校验 YAML
   - 校验失败时最多自动修复 `AUTO_FIX_ATTEMPTS` 次
   - 修复仍失败时返回最后 YAML 和 `validation.valid=false`

## 运行测试

在项目根目录执行：

```bash
python -m pytest backend/tests
```

真实 AI 手动 smoke test：

```bash
set ENABLE_AI_GENERATION=true
set MODEL_PROVIDER=openai
set MODEL_NAME=your-model-name
set MODEL_API_KEY=your-api-key
python backend/scripts/ai_smoke_test.py
```

该命令会真实调用模型，可能产生费用。小说内容会发送给模型供应商，运行前请确认授权和隐私风险。

## 请求示例

### 章节解析

```bash
curl -X POST http://127.0.0.1:8000/api/chapters/parse \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"第一章 雨夜来客\n正文一。\n第二章 旧案\n正文二。\n第三章 暗巷\n正文三。\"}"
```

### YAML 校验

```json
{
  "yaml": "script:\n  title: 长夜初逢\n  ..."
}
```

### 剧本生成

```json
{
  "title": "测试小说",
  "genre": "悬疑",
  "chapters": [
    {"id": "C001", "title": "第一章", "content": "正文一", "word_count": 3},
    {"id": "C002", "title": "第二章", "content": "正文二", "word_count": 3},
    {"id": "C003", "title": "第三章", "content": "正文三", "word_count": 3}
  ]
}
```

### 创建项目

```json
{
  "title": "长夜初逢",
  "genre": "悬疑",
  "source_content": "小说全文",
  "chapters": [],
  "yaml": "script:\n  title: ...",
  "validation": {"valid": true, "errors": []},
  "generation_mode": "mock"
}
```

### 导出

```text
GET /api/projects/{project_id}/export/yaml
GET /api/projects/{project_id}/export/json
GET /api/projects/{project_id}/export/markdown
```

## 项目结构

```
backend/
├── app/
│   ├── config/
│   │   └── settings.py          # 配置文件（新增 AI 配置）
│   ├── routers/
│   │   ├── chapters.py          # 章节解析路由
│   │   ├── projects.py          # 项目、版本和导出路由
│   │   └── script.py            # 剧本生成和校验路由
│   ├── services/
│   │   ├── chapter_parser.py    # 章节解析服务
│   │   ├── script_validator.py  # YAML 校验服务
│   │   ├── script_generator.py  # 剧本生成服务（已重构）
│   │   ├── ai_client.py         # AI 客户端（新增）
│   │   ├── export_service.py    # YAML/JSON/Markdown 导出
│   │   ├── project_service.py   # SQLite 项目和版本服务
│   │   └── prompt_loader.py     # Prompt 模板加载（新增）
│   ├── schemas/
│   │   ├── requests.py          # 请求模型
│   │   └── responses.py         # 响应模型
│   └── main.py                  # FastAPI 应用入口
├── tests/                       # 测试文件
├── scripts/                     # 手动 AI smoke test
├── requirements.txt             # Python 依赖
└── README.md                    # 本文件
```

## 说明

- **Mock 模式**：默认模式，返回 `examples/script-output-1.yaml`，不消耗 API 额度
- **AI 模式**：调用真实 AI 模型，需要配置 API Key 和环境变量；缺 Key、依赖缺失、模型返回 JSON/YAML 不合法或 Schema 校验失败时会返回明确错误或 invalid 校验结果
- Prompt 模板位于 `prompts/` 目录，可根据需要调整
- 第四阶段新增多类型示例小说和无效 YAML fixture，详见 `docs/testing-report.md`
- 第五阶段 AI 接入和测试说明见 `docs/ai-generation.md`、`docs/phase5-ai-test-report.md`
