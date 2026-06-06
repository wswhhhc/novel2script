# 项目结构说明

本文档描述 Novel2Script 项目的目录结构和文件组织。

## 📁 根目录

```
novel2script/
├── README.md                    # 项目主文档（含架构图、快速开始）
├── CLAUDE.md                    # 开发指南（给未来的开发者）
├── LICENSE                      # MIT 开源协议
├── .env.example                 # 环境变量模板
├── .gitignore                   # Git 忽略规则
├── docker-compose.yml           # Docker Compose 配置
├── Dockerfile.backend           # 后端容器构建文件
├── Dockerfile.frontend          # 前端容器构建文件
│
├── backend/                     # Python FastAPI 后端
├── frontend/                    # React TypeScript 前端
├── docs/                        # 项目文档
├── examples/                    # 示例数据
├── prompts/                     # AI Prompt 模板
├── schemas/                     # JSON Schema 定义
├── scripts/                     # 启动和测试脚本
├── submission/                  # 比赛提交材料
└── docker/                      # Docker 相关配置
```

---

## 🐍 backend/ - 后端目录

```
backend/
├── requirements.txt             # Python 依赖
│
├── app/                         # 应用代码
│   ├── __init__.py
│   ├── main.py                  # FastAPI 入口
│   │
│   ├── config/                  # 配置模块
│   │   ├── __init__.py
│   │   └── settings.py          # 环境变量、路径配置
│   │
│   ├── routers/                 # API 路由层
│   │   ├── __init__.py
│   │   ├── batch.py             # /api/batch/* 批量操作
│   │   ├── chapters.py          # /api/chapters/* 章节解析
│   │   ├── script.py            # /api/script/* 生成、校验和流式输出
│   │   └── projects.py          # /api/projects/* 项目、版本和导出
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── chapter_parser.py    # 章节识别
│   │   ├── script_generator.py  # 剧本生成（5阶段）
│   │   ├── script_validator.py  # YAML Schema 校验
│   │   ├── ai_client.py         # AI API 调用封装
│   │   ├── prompt_loader.py     # Prompt 模板加载
│   │   ├── project_service.py   # 项目 CRUD
│   │   ├── generation_cache.py  # AI 阶段缓存
│   │   ├── export_service.py    # YAML/JSON/Markdown 导出
│   │   └── pdf_export_service.py # PDF 导出
│   │
│   ├── schemas/                 # Pydantic 数据模型
│   │   ├── __init__.py
│   │   ├── requests.py          # 请求模型
│   │   ├── responses.py         # 响应模型
│   │   └── projects.py          # 项目模型
│   │
│   └── db/                      # 数据库层
│       ├── __init__.py
│       └── database.py          # SQLite 初始化
│
├── tests/                       # 测试代码
│   ├── conftest.py              # pytest 配置
│   ├── test_chapter_parser.py
│   ├── test_script_validator.py
│   ├── test_api.py
│   └── ...
│
├── scripts/                     # 辅助脚本
│   └── ai_smoke_test.py
│
└── data/                        # SQLite 数据库目录
    └── .gitignore               # 忽略数据库文件
```

---

## ⚛️ frontend/ - 前端目录

```
frontend/
├── package.json                 # npm 依赖和脚本
├── package-lock.json
├── .env.example                 # 前端环境变量
├── .gitignore
│
├── vite.config.ts               # Vite 构建配置
├── vitest.config.ts             # Vitest 测试配置
├── playwright.config.ts         # Playwright E2E 配置
├── tsconfig.json                # TypeScript 配置
├── tailwind.config.js           # Tailwind CSS 配置
├── postcss.config.js            # PostCSS 配置
├── index.html                   # HTML 入口
│
├── src/                         # 源代码
│   ├── main.tsx                 # React 入口
│   ├── App.tsx                  # 主应用组件
│   ├── styles.css               # 全局样式
│   ├── vite-env.d.ts
│   │
│   ├── api/                     # API 客户端
│   │   ├── client.ts            # 后端 API 调用函数
│   │   └── types.ts             # TypeScript 接口定义
│   │
│   ├── components/              # React 组件
│   │   ├── NovelInput.tsx       # 小说输入
│   │   ├── FileUpload.tsx       # 文件上传
│   │   ├── ChapterList.tsx      # 章节列表
│   │   ├── GenerationPanel.tsx  # 生成控制
│   │   ├── YamlEditor.tsx       # Monaco 编辑器
│   │   ├── ValidationPanel.tsx  # 校验结果
│   │   ├── ProjectSidebar.tsx   # 项目列表
│   │   ├── VersionHistory.tsx   # 版本历史
│   │   ├── ExportPanel.tsx      # 导出面板
│   │   ├── SaveProjectDialog.tsx
│   │   └── StatusBanner.tsx
│   │
│   └── utils/                   # 工具函数
│       ├── yaml.ts              # YAML 处理
│       ├── download.ts          # 下载工具
│       └── format.ts            # 格式化工具
│
├── scripts/                     # 前端脚本
│   └── smoke-test.mjs           # 前端 smoke test
│
├── e2e/                         # Playwright 端到端测试
│   └── workspace.spec.ts
│
└── dist/                        # 构建输出（自动生成）
```

---

## 📚 docs/ - 文档目录

```
docs/
├── requirements.md              # 需求文档
├── architecture-overview.md     # 架构设计
├── yaml-schema.md               # YAML Schema 设计说明
├── ai-generation.md             # AI 五阶段生成流程
├── comparison-report.md         # 对比实验报告
└── project-structure.md         # 项目结构说明
```

---

## 📝 examples/ - 示例数据

```
examples/
├── novel-sample-1.txt           # 都市小说 3 章（推荐演示）
├── novel-sample-2.txt           # 悬疑小说 5 章
├── novel-sample-3.txt           # 古装武侠 4 章
├── novel-edge-too-few-chapters.txt        # 边界测试：章节不足
├── novel-edge-mixed-chapter-formats.txt   # 边界测试：混合格式
│
├── script-output-1.yaml         # 标准 Mock 输出
├── invalid-script-missing-required.yaml   # 校验失败示例
└── invalid-script-bad-reference.yaml      # 校验失败示例
```

---

## 💬 prompts/ - AI Prompt 模板

```
prompts/
├── 01_chapter_analysis.txt      # 阶段1：章节分析
├── 02_character_extraction.txt  # 阶段2：角色提取
├── 03_scene_planning.txt        # 阶段3：场景规划
├── 04_script_generation.txt     # 阶段4：剧本生成
└── 05_yaml_fix.txt              # 阶段5：YAML 修复
```

**使用方式**：
- `prompt_loader.py` 加载这些模板
- 使用 `{title}`, `{genre}`, `{chapters}` 等占位符
- 在运行时替换为实际数据

---

## 📋 schemas/ - JSON Schema

```
schemas/
└── script.schema.json           # YAML 剧本的 JSON Schema（332 行）
```

**用途**：
- 定义剧本 YAML 的结构约束
- `script_validator.py` 使用此文件校验
- 包含 ID 格式、字段类型、长度限制等规则

---

## 🔨 scripts/ - 启动和测试脚本

```
scripts/
├── start-dev.ps1                # Windows 一键启动
├── start-dev.sh                 # macOS/Linux 一键启动
├── smoke-test.ps1               # Windows 端到端测试
├── smoke-test.sh                # macOS/Linux 端到端测试
├── reset-demo-data.ps1          # Windows 重置演示数据
└── reset-demo-data.sh           # macOS/Linux 重置演示数据
```

---

## 🏆 submission/ - 比赛提交材料

```
submission/
└── qa-handbook.md               # 答辩问答手册
```

---

## 🐳 docker/ - Docker 配置

```
docker/
└── nginx.conf                   # Nginx 反向代理配置（可选）
```

---

## 🔍 关键文件说明

### 配置文件
- `.env.example` - 环境变量模板，包含 AI 模型配置
- `docker-compose.yml` - 定义前后端容器和数据卷
- `.gitignore` - 排除 `.env`, `node_modules`, 数据库等

### 构建文件
- `Dockerfile.backend` - 后端 Python 环境
- `Dockerfile.frontend` - 前端静态文件构建

### 文档文件
- `README.md` - 主文档，包含快速开始和完整说明
- `CLAUDE.md` - 开发指南，给未来维护者的技术文档
- `LICENSE` - MIT 开源协议

---

## 🚫 不在版本控制中的文件

以下文件被 `.gitignore` 排除：

```
.env                             # 真实的 API Key
node_modules/                    # npm 依赖
frontend/dist/                   # 构建输出
backend/data/*.db                # SQLite 数据库
__pycache__/                     # Python 缓存
*.log                            # 日志文件
.pytest_cache/                   # pytest 缓存
frontend/test-results/           # Playwright 测试报告
```

---

## 📊 项目统计

- **总文件数**：约 120 个（不含 node_modules）
- **代码行数**：约 20,000 行
- **文档数量**：约 10 个（README + CLAUDE + docs/* + submission/*）
- **测试体系**：后端 pytest、前端 Vitest、Playwright E2E、smoke test

---

## 🎯 目录设计原则

1. **关注点分离**：前后端、文档、示例、脚本分离
2. **清晰命名**：目录和文件名一目了然
3. **标准结构**：遵循 FastAPI 和 React 最佳实践
4. **易于导航**：README 包含完整导航链接
5. **适合协作**：清晰的模块划分便于多人开发

---

## 🔗 相关文档

- [README.md](../README.md) - 项目主文档
- [CLAUDE.md](../CLAUDE.md) - 开发指南
- [docs/architecture-overview.md](architecture-overview.md) - 架构详解
