# 第五阶段 AI 生成测试报告

## 测试范围

第五阶段围绕真实 AI 生成链路稳定化补充测试：

- Mock 模式仍可生成示例 YAML。
- AI 模式缺少 API Key 时返回清晰错误。
- Prompt loader 不再依赖 `.format()`，支持 5 个模板安全替换变量。
- 阶段 1-3 JSON 解析支持直接 JSON 和 Markdown `json` 代码块。
- 阶段 4-5 YAML 提取支持直接 YAML、Markdown `yaml` 代码块和 YAML 前后说明文本。
- 使用 fake AI responses 覆盖完整生成、非法 YAML 自动修复成功、修复失败返回 invalid。
- AI 客户端在未启用或缺 Key 时不会发起真实网络请求。

## 自动化测试命令

```bash
python -m pytest backend/tests
cd frontend
npm run smoke
npm run build
```

默认测试不需要真实 API Key，不会调用模型供应商。

## 手动真实 AI smoke test

```bash
set ENABLE_AI_GENERATION=true
set MODEL_PROVIDER=openai
set MODEL_NAME=your-model-name
set MODEL_API_KEY=your-api-key
python backend/scripts/ai_smoke_test.py
```

该测试会真实调用模型，可能产生费用，并会把生成结果写入 `backend/scripts/ai-smoke-output.yaml`。

## 当前限制

- 长章节在 AI prompt 中保留前后关键片段并省略中间内容，适合 MVP 稳定性，但不是完整长文本分块总结。
- Anthropic 支持为可选扩展，默认依赖只保证 OpenAI 兼容接口。
- 真实改编质量仍需要人工验收，自动化测试主要验证结构、错误处理和修复链路。
