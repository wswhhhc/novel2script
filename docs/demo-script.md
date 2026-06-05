# Novel2Script 演示脚本

## 3-5 分钟演示流程

演示目标：证明项目可以完成“小说输入 -> 章节识别 -> Mock 生成 YAML 剧本 -> 编辑校验 -> 保存版本 -> 多格式导出”的闭环。

推荐示例：

```text
examples/novel-sample-1.txt
```

## 演示前准备

1. 启动项目：

```powershell
scripts/start-dev.ps1
```

2. 打开前端：

```text
http://127.0.0.1:5173
```

3. 确认后端健康：

```text
http://127.0.0.1:8000/health
```

## 点击步骤

1. 在工作台填写标题：`长夜初逢`。
2. 类型填写：`都市`。
3. 上传或粘贴 `examples/novel-sample-1.txt`。
4. 点击“识别章节”。
5. 展示识别结果：3 个章节、章节 ID、标题和字数。
6. 点击“生成剧本”。
7. 说明当前为 Mock 模式：不依赖 API Key，适合稳定演示。
8. 展示 YAML 编辑器中的结构：`script`、`source`、`characters`、`scenes`、`adaptation_notes`、`open_questions`。
9. 点击“重新校验”，展示 Schema 校验通过。
10. 修改一小处 YAML 文本，再次校验，说明可编辑。
11. 点击保存，创建本地项目。
12. 在版本历史中保存快照。
13. 展示恢复版本入口。
14. 导出 YAML、JSON、Markdown。

## AI 模式说明

演示时不强制调用真实 AI。只展示配置方式：

```env
ENABLE_AI_GENERATION=true
MODEL_PROVIDER=openai
MODEL_NAME=your-model-name
MODEL_API_KEY=your-api-key
MODEL_BASE_URL=https://api.openai.com/v1
```

说明要点：

- Mock 模式默认开启，不产生费用，不发送小说内容。
- AI 模式会把小说章节发送给模型供应商。
- 真实 AI 质量受模型、Prompt、输入文本影响，需要人工复核。
- 后端会对 AI 输出执行 YAML Schema 校验和自动修复。

## 备用方案

- 如果前端页面不可用：用 `scripts/smoke-test.ps1` 展示后端主流程结果。
- 如果端口占用：释放 8000 / 5173 后重启。
- 如果 AI 模式不可用：切回 Mock 模式，说明默认验收不依赖真实 API Key。
- 如果导出失败：先保存项目并确认 YAML 可校验通过。
- 如果浏览器缓存旧配置：刷新页面，确认 `VITE_API_BASE_URL` 指向 `http://127.0.0.1:8000`。
