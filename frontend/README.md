# Novel2Script Frontend

前端工作台基于 React、Vite、TypeScript、Tailwind CSS、Monaco Editor 和 js-yaml 实现，支持章节识别、剧本生成、YAML 编辑校验、项目保存、版本快照和多格式导出。

## 启动后端

在项目根目录执行：

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --app-dir backend
```

后端默认地址：

```text
http://127.0.0.1:8000
```

## 启动前端

在 `frontend/` 目录执行：

```bash
npm install
npm run dev
```

前端默认地址：

```text
http://127.0.0.1:5173
```

## 环境变量

复制 `.env.example` 为 `.env` 后可调整：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_MAX_FILE_SIZE=10485760
VITE_SUPPORTED_FORMATS=.txt,.md
```

## 基础流程

1. 填写小说标题和类型。
2. 粘贴小说正文，或上传 `.txt` / `.md` 文件。
3. 点击“识别章节”。
4. 章节数量满足要求后点击“生成剧本”。
5. 在 YAML 编辑区查看和修改内容。
6. 点击“重新校验”检查 YAML。
7. 点击“保存”将当前小说、章节、YAML 和校验结果保存到后端 SQLite。
8. 在“版本历史”中保存快照；需要回滚时点击对应版本的恢复按钮。
9. 使用顶部导出入口下载 YAML、JSON 或 Markdown。

## 项目与导出

- 项目列表位于工作台左侧，可打开、刷新、新建或删除本地项目。
- 首次保存会要求填写项目标题和类型，再次保存会更新当前项目。
- “另存为”会基于当前工作台内容创建新项目。
- 导出依赖已保存项目；无效 YAML 在导出 JSON / Markdown 时会显示后端错误。
- SQLite 数据文件由后端维护，默认位置为 `backend/data/novel2script.db`。

## 测试与构建

```bash
npm run smoke
npm run build
```

`npm run smoke` 会检查关键前端保护点，包括章节 invalid 时禁用生成、warnings 警告展示、YAML 校验错误列表、编辑后不清空用户内容、上传文件类型和大小限制，以及项目保存、项目列表、版本历史和三种导出入口。
