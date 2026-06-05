# Novel2Script 项目摘要

## 一句话介绍

Novel2Script 是一个把小说章节转换为结构化 YAML 剧本初稿的 AI 辅助创作工具。

## 解决的问题

小说改编剧本需要重新组织场景、角色、对白和动作，门槛较高且耗时。Novel2Script 通过章节识别、结构化生成和 Schema 校验，帮助作者快速得到可编辑、可追溯、可导出的剧本初稿。

## 目标用户

- 小说作者
- 编剧初学者
- 短剧创作者
- 内容团队和 IP 改编评估人员

## 核心功能

- 小说输入和文件上传。
- 自动章节识别。
- Mock / AI 剧本生成。
- YAML Schema 校验。
- YAML 编辑和下载。
- 本地项目保存。
- 版本快照和恢复。
- YAML / JSON / Markdown 导出。

## 技术栈

- 后端：Python、FastAPI、Pydantic、PyYAML、jsonschema、SQLite。
- 前端：React、TypeScript、Vite、Tailwind CSS、Monaco Editor。
- 部署：本地启动脚本、Docker Compose。

## 创新点

- 将小说改编结果约束为可校验 YAML，而不是只输出散文式文本。
- 保留章节到场景的来源追溯。
- 用角色 ID 和场景 ID 减少人物引用混乱。
- Mock 模式保证演示稳定，AI 模式支持真实生成链路。

## 当前完成度

项目已完成 MVP 主流程、AI 模式接入、本地项目保存、版本管理、多格式导出、自动化测试、部署脚本、Docker Compose 和最终答辩材料。
