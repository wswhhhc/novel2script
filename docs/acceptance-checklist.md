# Novel2Script 最终验收清单

## 基础服务

- [ ] 后端健康检查通过：`GET /health`
- [ ] 前端首页可访问：`http://127.0.0.1:5173`
- [ ] 默认进入工作台页面，而不是营销页
- [ ] Mock 模式无需 API Key 可运行
- [ ] AI 模式缺少 API Key 时错误清晰

## 主流程

- [ ] `examples/novel-sample-1.txt` 可识别 3 个章节
- [ ] 章节不足示例会提示数量不足
- [ ] Mock 生成返回非空 YAML
- [ ] YAML 校验通过
- [ ] YAML 编辑后可重新校验
- [ ] 错误 YAML 可显示具体错误列表

## 项目与导出

- [ ] 可创建本地项目
- [ ] 可打开项目列表中的项目
- [ ] 可更新项目
- [ ] 可创建 YAML 版本快照
- [ ] 可查看版本历史
- [ ] 可恢复历史版本
- [ ] 可导出 YAML
- [ ] 可导出 JSON
- [ ] 可导出 Markdown

## 前端可用性

- [ ] 桌面端按钮和主要文本不溢出
- [ ] 移动端可以完成输入、识别、生成、校验、保存
- [ ] 请求失败提示可读
- [ ] 保存、版本、导出入口含义清楚
- [ ] Mock / AI 模式说明不误导用户

## 测试命令

```bash
python -m pytest backend/tests
```

```bash
cd frontend
npm run smoke
npm run build
```

后端和前端启动后：

```powershell
scripts/smoke-test.ps1
```

## Docker

- [ ] `docker compose up --build` 可构建并启动
- [ ] 后端容器暴露 `8000`
- [ ] 前端容器暴露 `5173`
- [ ] SQLite 数据使用 volume 持久化
- [ ] Compose 文件不包含真实 API Key

## 安全与提交

- [ ] 不提交真实 `.env`
- [ ] 不提交真实 API Key
- [ ] 不提交 SQLite `.db`
- [ ] 不提交 `node_modules/`
- [ ] 不提交 `frontend/dist/`
- [ ] 不提交临时日志和缓存
- [ ] `.gitignore` 覆盖运行时产物
