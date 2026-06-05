# Novel2Script 最终部署说明

## 1. 本地启动

推荐 Windows PowerShell：

```powershell
scripts/start-dev.ps1
```

macOS / Linux：

```bash
bash scripts/start-dev.sh
```

脚本会检查 Python、Node.js、npm 和端口占用。默认端口：

- 后端：http://127.0.0.1:8000
- 前端：http://127.0.0.1:5173

如果脚本提示端口占用，先停止占用进程，或手动启动并指定其他端口。

手动启动命令：

```bash
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --reload --app-dir backend --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

## 2. Docker Compose 启动

```bash
cp .env.example .env
docker compose --project-name novel2script up --build
```

服务：

- `backend`：FastAPI，映射 `8000:8000`
- `frontend`：Nginx 静态站点，映射 `5173:80`
- `novel2script-data`：SQLite 数据 volume

访问：

- http://127.0.0.1:5173
- http://127.0.0.1:8000/health

默认 Mock 模式可直接运行，不需要 API Key。

如果项目路径包含空格或非 ASCII 字符，建议始终显式传入 `--project-name novel2script`。

## 3. 环境变量

根目录 `.env.example` 是最终配置模板。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `ENABLE_AI_GENERATION` | `false` | 是否启用真实 AI |
| `MODEL_PROVIDER` | `openai` | 模型供应商 |
| `MODEL_NAME` | 空 | AI 模式必填 |
| `MODEL_API_KEY` | 空 | AI 模式必填，禁止提交 |
| `MODEL_BASE_URL` | `https://api.openai.com/v1` | OpenAI 兼容接口地址 |
| `MODEL_TEMPERATURE` | `0.7` | 生成温度 |
| `MODEL_MAX_TOKENS` | `4000` | 最大输出 token |
| `MODEL_TIMEOUT` | `120` | 模型请求超时秒数 |
| `AUTO_FIX_ATTEMPTS` | `3` | YAML 自动修复次数 |
| `NOVEL2SCRIPT_DB_PATH` | `backend/data/novel2script.db` | SQLite 文件位置 |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | 前端请求后端地址 |

Mock 模式无需 API Key。AI 模式会将小说内容发送给模型供应商，需要确认授权、隐私和费用风险。

## 4. 数据持久化

本地开发默认数据库：

```text
backend/data/novel2script.db
```

Docker Compose 使用 volume：

```text
novel2script-data -> /app/backend/data
```

重置演示数据：

```powershell
scripts/reset-demo-data.ps1
```

```bash
bash scripts/reset-demo-data.sh
```

## 5. 端口说明

- 后端 API：`8000`
- 前端页面：本地开发 `5173`，Docker Compose 映射到 `5173`

后端 CORS 已允许：

- `http://127.0.0.1:5173`
- `http://localhost:5173`

## 6. 常见部署问题

- `python` 不可用：安装 Python 3.10+ 并加入 PATH。
- `npm` 不可用：安装 Node.js 18+。
- 端口占用：释放 8000 / 5173，或改端口并同步配置。
- Docker 前端请求后端失败：确认浏览器所在机器可访问 `http://127.0.0.1:8000`。
- `project name must not be empty`：使用 `docker compose --project-name novel2script ...`。
- 无法连接 Docker API：启动 Docker Desktop 或对应 Docker daemon 后重试。
- AI 模式失败：确认 `ENABLE_AI_GENERATION=true`，并配置 `MODEL_NAME`、`MODEL_API_KEY`、`MODEL_BASE_URL`。
- 不要提交 `.env`、SQLite `.db`、日志、`node_modules` 或 `frontend/dist`。
