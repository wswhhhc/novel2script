# Novel2Script 部署与演示说明

## 项目结构

```text
backend/      FastAPI 后端，提供章节解析、剧本生成、YAML 校验接口
frontend/     React + Vite 前端工作台
prompts/      AI 分阶段生成 Prompt 模板
schemas/      YAML JSON Schema
examples/     示例小说、标准 YAML、无效 YAML fixture
docs/         需求、Schema、测试与部署文档
```

## 后端安装与启动

在项目根目录执行：

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

默认地址：

```text
http://127.0.0.1:8000
```

健康检查：

```text
http://127.0.0.1:8000/health
```

MVP 默认使用 Mock 模式，不调用真实 AI。需要真实 AI 时再配置：

```env
ENABLE_AI_GENERATION=true
MODEL_PROVIDER=openai
MODEL_NAME=your-model-name
MODEL_API_KEY=your-api-key
MODEL_BASE_URL=https://api.openai.com/v1
MODEL_TEMPERATURE=0.7
MODEL_MAX_TOKENS=4000
MODEL_TIMEOUT=120
MODEL_MAX_RETRIES=2
AUTO_FIX_ATTEMPTS=3
```

## 前端安装与启动

在 `frontend/` 目录执行：

```bash
npm install
npm run dev
```

默认地址：

```text
http://127.0.0.1:5173
```

前端环境变量可从 `frontend/.env.example` 复制：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_MAX_FILE_SIZE=10485760
VITE_SUPPORTED_FORMATS=.txt,.md
```

## 测试命令

后端自动化测试：

```bash
python -m pytest backend/tests
```

前端 smoke test：

```bash
cd frontend
npm run smoke
```

前端生产构建：

```bash
cd frontend
npm run build
```

## 主流程演示

1. 启动后端和前端。
2. 在前端填写标题和类型。
3. 上传或粘贴 `examples/novel-sample-1.txt`。
4. 点击“识别章节”，确认识别到 3 章且状态有效。
5. 点击“生成剧本”，Mock 模式会返回 `examples/script-output-1.yaml`。
6. 在 YAML 编辑器中点击“校验”，确认 Schema 校验通过。
7. 点击“下载”导出 YAML。

## 常见问题

- CORS 报错：确认后端已启动在 `http://127.0.0.1:8000`，前端 `.env` 中 `VITE_API_BASE_URL` 与后端地址一致。
- 端口占用：后端可改用 `uvicorn app.main:app --reload --app-dir backend --port 8001`，同时更新前端 `.env`。
- 依赖安装失败：先确认 Python 3.10+、Node.js 18+ 可用；Windows 下可尝试用管理员终端重新安装依赖。
- 生成结果始终相同：默认是 Mock 模式，适合演示和测试；启用 AI 需要设置 `ENABLE_AI_GENERATION=true` 和 API Key。
- 上传失败：MVP 只支持 `.txt` 和 `.md`，默认最大 10MB。
