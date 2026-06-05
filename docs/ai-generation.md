# AI 生成链路说明

## 模式

Novel2Script 保留两种生成模式：

- Mock 模式：默认模式，不调用真实模型，返回示例 YAML，适合演示、联调和自动化测试。
- AI 模式：调用 OpenAI 兼容 Chat Completions API，执行章节分析、角色提取、场景规划、剧本 YAML 生成和 YAML 修复。

## OpenAI 兼容 API 配置

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

`MODEL_NAME` 必须由环境变量提供，项目不会硬编码某个模型。`MODEL_BASE_URL` 可替换为兼容 OpenAI Chat Completions 的服务地址。

## 依赖

默认后端依赖已包含 `openai`。Anthropic 作为可选扩展保留，如果使用：

```bash
pip install anthropic
```

## 启动

Mock 模式：

```bash
uvicorn app.main:app --reload --app-dir backend
```

AI 模式：

```bash
set ENABLE_AI_GENERATION=true
set MODEL_PROVIDER=openai
set MODEL_NAME=your-model-name
set MODEL_API_KEY=your-api-key
uvicorn app.main:app --reload --app-dir backend
```

前端会读取 `GET /api/script/mode` 并显示当前生成模式。

## 测试

默认自动化测试不需要真实 API Key，也不会产生模型费用：

```bash
python -m pytest backend/tests
cd frontend
npm run smoke
npm run build
```

真实 AI 手动 smoke test 只在显式配置 API Key 后运行：

```bash
set ENABLE_AI_GENERATION=true
set MODEL_PROVIDER=openai
set MODEL_NAME=your-model-name
set MODEL_API_KEY=your-api-key
python backend/scripts/ai_smoke_test.py
```

该脚本会把结果写入 `backend/scripts/ai-smoke-output.yaml`，可能产生费用。

## 常见错误

- `MODEL_API_KEY` 缺失：AI 模式已开启但没有配置密钥。
- 依赖缺失：未安装 `openai` 或可选的 `anthropic`。
- JSON 不合法：阶段 1-3 返回内容不是合法 JSON。
- YAML 不合法：阶段 4-5 返回内容无法提取 `script` 顶层字段或 YAML 解析失败。
- Schema 校验失败：自动修复会尝试 `AUTO_FIX_ATTEMPTS` 次；仍失败时接口返回最后 YAML，并设置 `validation.valid=false`。

## 成本与隐私

AI 模式会把小说章节内容发送给模型供应商。运行前应确认文本授权、供应商隐私政策和费用风险。不要把真实 API Key 写入代码、测试或公开文档。
