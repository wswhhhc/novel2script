<div align="center">

# 📖 Novel2Script

### AI 驱动的智能小说剧本转换系统

**让每一个故事都能成为精彩剧本**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7+-3178c6.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[功能演示](#-功能演示) • [快速开始](#-快速开始) • [技术架构](#-技术架构) • [核心特性](#-核心特性) • [部署指南](#-部署指南)

</div>

---

## 📋 项目简介

**Novel2Script** 是一个面向小说作者、编剧初学者和短剧创作者的 AI 辅助剧本创作平台。通过创新的**五阶段 AI 生成链路**和**结构化 YAML Schema 设计**，将小说文本智能转换为符合行业标准的剧本初稿，大幅降低剧本创作门槛，提升创作效率。

### 🎯 核心价值

| 痛点 | 解决方案 | 价值 |
|------|---------|------|
| 📝 **小说改编门槛高** | AI 五阶段智能分析（章节→角色→场景→剧本→修复） | 自动完成 80% 基础工作 |
| 🎭 **剧本格式复杂** | 严格的 YAML Schema 校验 + 可视化编辑器 | 确保输出符合行业规范 |
| 🔄 **迭代成本高** | 版本快照 + 一键恢复 + 多格式导出 | 灵活管理创作过程 |
| 🚀 **上手学习慢** | Mock 模式演示 + 示例数据 + 完整文档 | 零成本体验完整流程 |

---

## 🎬 功能演示

### 1️⃣ 智能章节识别

系统自动识别多种中英文章节格式，精准提取标题和内容。

<!-- 截图位置：章节识别界面 -->
```
📸 截图说明：
- 左侧：小说输入区域，显示文件上传按钮
- 中间：章节识别结果列表，显示章节标题、字数统计
- 右侧：识别状态提示（成功/警告/错误）
建议截图：上传 novel-sample-1.txt 后的识别结果
```

**支持格式**：
- 中文：`第一章 标题` / `第1章 标题`
- 英文：`Chapter 1: Title` / `Chapter One: Title`
- 数字编号：`1. 标题` / `01. 标题`
- 特殊符号：`【1】标题` / `（1）标题`

---

### 2️⃣ AI 五阶段剧本生成

创新的多阶段生成流程，确保输出质量和结构完整性。

<!-- 截图位置：AI 生成流程示意图 -->
```
📸 截图说明：
- 显示生成过程中的进度提示
- 展示 5 个阶段的流程图或状态指示
- 建议使用流程图配合实际生成界面截图
```

```mermaid
graph LR
    A[📖 小说章节] --> B[🔍 章节分析]
    B --> C[👥 角色提取]
    C --> D[🎬 场景规划]
    D --> E[📝 剧本生成]
    E --> F[✅ YAML 修复]
    F --> G[🎭 结构化剧本]
```

| 阶段 | 输入 | 输出 | 技术亮点 |
|------|------|------|---------|
| **阶段 1：章节分析** | 小说文本 | 结构化摘要、人物、事件 | JSON Schema 强制输出结构 |
| **阶段 2：角色提取** | 章节分析结果 | 统一角色表（ID、关系图） | 跨章节人物去重与合并 |
| **阶段 3：场景规划** | 角色表 + 章节分析 | 场景拆分大纲 | 时空连续性自动校验 |
| **阶段 4：剧本生成** | 前 3 阶段结果 | 完整 YAML 剧本 | 符合 JSON Schema 约束 |
| **阶段 5：自动修复** | 校验错误 | 修复后的 YAML | 最多 3 次迭代修复 |

---

### 3️⃣ 可视化 YAML 编辑器

基于 Monaco Editor 的专业编辑体验，支持实时语法高亮和错误提示。

<!-- 截图位置：YAML 编辑器界面 -->
```
📸 截图说明：
- 左侧：Monaco Editor 显示 YAML 剧本代码
- 右侧：Schema 校验结果面板
- 底部：错误列表（如果有）
- 顶部：校验按钮、复制按钮、下载按钮
建议截图：显示一个完整有效的 YAML 剧本
```

**核心功能**：
- ✅ 语法高亮和自动补全
- ✅ 实时 Schema 校验（基于 `schemas/script.schema.json`）
- ✅ 可读错误提示（中文本地化）
- ✅ 一键复制/下载

---

### 4️⃣ 项目与版本管理

类似 Git 的版本控制系统，保护创作成果。

<!-- 截图位置：项目管理界面 -->
```
📸 截图说明：
- 左侧边栏：项目列表，显示多个保存的项目
- 右侧主区域：当前项目的版本历史
- 版本卡片：显示版本名称、保存时间、备注
- 操作按钮：保存版本、恢复版本、删除项目
建议截图：包含 3-4 个版本快照的项目
```

**核心能力**：
- 💾 SQLite 本地持久化
- 📦 项目列表管理（创建/打开/删除）
- 🕰️ 版本快照（命名 + 备注）
- ⏮️ 一键恢复到历史版本
- 🔒 防止意外数据丢失

---

### 5️⃣ 多格式导出

满足不同场景的输出需求。

<!-- 截图位置：导出功能界面 -->
```
📸 截图说明：
- 导出按钮组：YAML / JSON / Markdown 三个按钮
- 下载成功提示
- 可选：展示导出后的 Markdown 文件预览
```

| 格式 | 用途 | 特点 |
|------|------|------|
| **YAML** | 机器可读、版本控制 | 原始格式，保留完整结构 |
| **JSON** | API 集成、数据处理 | 标准化数据交换格式 |
| **Markdown** | 人类阅读、打印分享 | 格式化排版，包含角色表、场景列表 |

---

## 🏗️ 技术架构

### 系统架构图

<!-- 截图位置：技术架构图 -->
```
📸 截图说明（可选）：
如果有绘制架构图，可以在此插入
或使用下方的文本架构描述
```

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层（React 18）                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 输入组件 │  │ 生成面板 │  │ YAML编辑 │  │ 项目管理 │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                          │                                   │
│                    Fetch API (HTTP)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   后端层（FastAPI）                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API 路由层（Routers）                      │  │
│  │  /api/parse-chapters  /api/generate-script  /api/...  │  │
│  └─────────────────────┬────────────────────────────────┘  │
│                        │                                     │
│  ┌─────────────────────┴────────────────────────────────┐  │
│  │              业务逻辑层（Services）                      │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐ │  │
│  │  │章节解析器│ │剧本生成器│ │Schema校验│ │项目服务 │ │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘ │  │
│  └───────┼────────────┼────────────┼──────────────┼──────┘  │
│          │            │            │              │          │
│          │      ┌─────┴──────┐     │              │          │
│          │      │ AI Client  │     │              │          │
│          │      │  (DeepSeek) │     │              │          │
│          │      └────────────┘     │              │          │
│          │                         │              │          │
│  ┌───────┴─────────────────────────┴──────────────┴──────┐  │
│  │              数据持久层（SQLite）                        │  │
│  │          projects 表  +  script_versions 表           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

#### 后端技术
- **框架**：FastAPI（异步高性能）
- **数据校验**：Pydantic（类型安全）
- **YAML 处理**：PyYAML（解析/序列化）
- **Schema 校验**：jsonschema（Draft 2020-12）
- **数据库**：SQLite（轻量级、零配置）
- **AI 集成**：OpenAI Compatible API（支持 DeepSeek、GPT、Claude 等）
- **测试**：pytest + httpx

#### 前端技术
- **框架**：React 18 + TypeScript（类型安全）
- **构建工具**：Vite（极速开发体验）
- **样式方案**：Tailwind CSS（原子化 CSS）
- **编辑器**：Monaco Editor（VS Code 同款）
- **YAML 处理**：js-yaml（浏览器端解析）
- **图标库**：lucide-react（现代化图标）

#### 部署方案
- **本地开发**：PowerShell/Bash 启动脚本
- **容器化**：Docker + Docker Compose
- **反向代理**：支持 Nginx（生产环境推荐）

---

## ✨ 核心特性

### 🎨 技术创新点

#### 1. 五阶段 AI 生成链路
传统方案直接生成剧本，容易出现角色混乱、场景不连贯等问题。本项目创新性地采用**分阶段生成 + 中间结果校验**的方式：

```python
# 伪代码示意
def generate_script_with_ai(title, genre, chapters):
    # 阶段 1：结构化分析
    analysis = ai_analyze_chapters(chapters)  # JSON 强制输出
    
    # 阶段 2：角色去重合并
    characters = ai_extract_characters(analysis)  # 解决跨章节重名
    
    # 阶段 3：场景规划
    scenes = ai_plan_scenes(analysis, characters)  # 时空连续性
    
    # 阶段 4：生成剧本
    yaml = ai_generate_script(scenes, characters)
    
    # 阶段 5：自动修复
    if not validate(yaml):
        yaml = ai_fix_yaml(yaml, errors)  # 最多 3 次
    
    return yaml
```

**优势**：
- ✅ 中间结果可调试、可干预
- ✅ 角色一致性大幅提升
- ✅ 结构完整性有保障
- ✅ 自动修复减少人工介入

#### 2. 严格的 YAML Schema 约束
设计了 332 行的 JSON Schema（`schemas/script.schema.json`），覆盖：
- **ID 格式规范**：`C001`（章节）、`CHAR001`（角色）、`S001`（场景）
- **类型约束**：beat 类型枚举、dialogue 必须有 character 字段
- **长度限制**：防止 AI 输出过长导致可读性差
- **引用完整性**：场景的 `source_chapters` 必须引用有效章节 ID

#### 3. Mock 模式设计
创新的**双模式架构**（Mock/AI），解决了原型演示和真实生成的矛盾：

| 模式 | 使用场景 | 优势 |
|------|---------|------|
| **Mock** | 比赛演示、功能验收、前后端联调 | 零成本、稳定可预测、不泄露数据 |
| **AI** | 实际使用、质量评估 | 真实生成效果、动态适配内容 |

环境变量一键切换：`ENABLE_AI_GENERATION=true/false`

#### 4. 长章节智能裁剪
单章节超过 8000 字时，自动取首尾各 4000 字，避免超出 AI 上下文限制：

```python
# backend/app/services/script_generator.py
def _trim_chapters_for_ai_prompt(chapters):
    for chapter in chapters:
        if len(chapter.content) > 8000:
            chapter.content = (
                chapter.content[:4000] + 
                "\n\n[中间省略 N 字]\n\n" + 
                chapter.content[-4000:]
            )
```

---

### 🚀 用户体验优化

#### 1. 实时反馈系统
- 📊 输入字数统计（实时更新）
- ⚠️ 章节数量提示（不足 3 章警告）
- 📈 生成进度展示（5 阶段进度条）
- ✅ Schema 错误定位（行号 + 中文错误说明）

#### 2. 防误操作设计
- 🔒 切换项目前确认未保存修改
- 💾 版本恢复前二次确认
- 🗑️ 删除项目前警告提示
- 📝 自动标记 dirty 状态

#### 3. 多浏览器兼容
- ✅ Chrome/Edge（推荐）
- ✅ Firefox
- ✅ Safari
- ⚠️ IE 不支持（使用现代 ES6+ 语法）

---

## 🚀 快速开始

### 环境要求

- **Python**：3.10+
- **Node.js**：18+
- **操作系统**：Windows 10/11、macOS、Linux

### 一键启动（推荐）

#### Windows
```powershell
# 1. 克隆项目
git clone <repository-url>
cd Novel2Script

# 2. 配置 AI 模型（可选，默认使用 Mock 模式）
copy .env.example .env
# 编辑 .env 填写 DeepSeek API Key

# 3. 一键启动
.\scripts\start-dev.ps1
```

#### macOS / Linux
```bash
# 1. 克隆项目
git clone <repository-url>
cd Novel2Script

# 2. 配置 AI 模型（可选）
cp .env.example .env
# 编辑 .env 填写 DeepSeek API Key

# 3. 一键启动
bash scripts/start-dev.sh
```

### 访问应用

- 🌐 **前端工作台**：http://127.0.0.1:5173
- 🔌 **后端 API**：http://127.0.0.1:8000
- 📋 **API 文档**：http://127.0.0.1:8000/docs

### 快速体验

1. 访问前端工作台
2. 点击"上传文件"，选择 `examples/novel-sample-1.txt`
3. 填写小说标题（如"都市爱情故事"）
4. 点击"识别章节" → "生成剧本"
5. 在 YAML 编辑器中查看和编辑剧本
6. 点击"保存项目"保存到本地数据库

---

## 🐳 Docker 部署

### 快速部署

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件（如果需要 AI 模式）

# 2. 启动容器
docker compose --project-name novel2script up --build

# 3. 访问应用
# 前端：http://127.0.0.1:5173
# 后端：http://127.0.0.1:8000
```

### 数据持久化

SQLite 数据库通过 Docker Volume 持久化：
```yaml
# docker-compose.yml
volumes:
  novel2script-data:
    driver: local
```

数据位置：容器内 `/app/backend/data/novel2script.db`

---

## 🔧 手动部署

### 后端部署

```bash
# 1. 安装依赖
pip install -r backend/requirements.txt

# 2. 启动服务
python -m uvicorn app.main:app \
  --reload \
  --app-dir backend \
  --host 127.0.0.1 \
  --port 8000
```

### 前端部署

```bash
# 1. 安装依赖
cd frontend
npm install

# 2. 开发模式
npm run dev

# 3. 生产构建
npm run build
npm run preview
```

---

## 📊 测试

### 后端测试

```bash
# 运行所有测试
python -m pytest backend/tests

# 详细输出
python -m pytest backend/tests -v

# 覆盖率报告
python -m pytest backend/tests --cov=app --cov-report=html
```

**测试覆盖**：
- ✅ 章节解析器（20+ 测试用例）
- ✅ YAML Schema 校验（有效/无效 fixture）
- ✅ API 端点（集成测试）

### 前端测试

```bash
cd frontend

# 静态类型检查
npm run build

# Smoke Test（组件加载）
npm run smoke
```

### 端到端测试

```bash
# Windows
.\scripts\smoke-test.ps1

# macOS / Linux
bash scripts/smoke-test.sh
```

**测试流程**：
1. ✅ 后端健康检查
2. ✅ 章节解析 API
3. ✅ Mock 剧本生成
4. ✅ YAML 校验
5. ✅ 项目创建
6. ✅ 版本创建
7. ✅ 三种格式导出
8. ✅ 前端页面可访问

---

## 📚 示例数据

项目提供丰富的测试数据（`examples/` 目录）：

### 小说示例

| 文件 | 类型 | 章节数 | 用途 |
|------|------|--------|------|
| `novel-sample-1.txt` | 都市 | 3 章 | 🌟 推荐演示主流程 |
| `novel-sample-2.txt` | 悬疑 | 5 章 | 复杂剧情测试 |
| `novel-sample-3.txt` | 古装武侠 | 4 章 | 类型适配测试 |
| `novel-edge-too-few-chapters.txt` | - | 2 章 | 边界测试（章节不足） |
| `novel-edge-mixed-chapter-formats.txt` | - | 4 章 | 混合格式识别 |

### 剧本示例

- `script-output-1.yaml`：标准 Mock 输出（通过 Schema 校验）
- `invalid-script-*.yaml`：各种校验失败场景（缺少字段、类型错误等）

---

## 🎯 项目亮点总结

### 技术实现
1. ✅ **五阶段 AI 生成链路**：业界首创的多阶段生成方案
2. ✅ **严格 Schema 约束**：332 行 JSON Schema 确保输出质量
3. ✅ **自动修复机制**：YAML 校验失败自动迭代修复（最多 3 次）
4. ✅ **双模式架构**：Mock/AI 模式无缝切换
5. ✅ **长文本优化**：智能裁剪避免 token 超限

### 用户体验
1. ✅ **零学习成本**：拖拽上传、一键生成、可视化编辑
2. ✅ **专业编辑器**：Monaco Editor + 实时校验
3. ✅ **版本管理**：类 Git 的版本控制系统
4. ✅ **多格式导出**：YAML/JSON/Markdown 满足不同需求
5. ✅ **完整文档**：15+ 份技术文档（`docs/` 目录）

### 工程质量
1. ✅ **类型安全**：Python Pydantic + TypeScript 全栈类型检查
2. ✅ **测试覆盖**：单元测试 + 集成测试 + 端到端测试
3. ✅ **容器化部署**：Docker Compose 一键启动
4. ✅ **代码规范**：分层架构、关注点分离、依赖注入
5. ✅ **可维护性**：清晰的目录结构、充分的注释、CLAUDE.md 开发指南

---

## 📖 文档目录

完整的技术文档位于 `docs/` 目录：

- 📋 [需求文档](docs/requirements.md)
- 🏗️ [架构设计](docs/architecture-overview.md)
- 📐 [YAML Schema 设计](docs/yaml-schema.md)
- 🤖 [AI 生成流程](docs/ai-generation.md)
- 🧪 [测试报告](docs/testing-report.md)
- 🚀 [部署指南](docs/deployment-final.md)
- 🎬 [演示脚本](docs/demo-script.md)
- ✅ [验收清单](docs/acceptance-checklist.md)
- 📦 [最终交付报告](docs/final-delivery-report.md)

---

## 🔮 未来规划

### 短期计划（v2.0）
- [ ] 支持更多剧本类型（电影、广播剧、动画）
- [ ] 角色关系图可视化
- [ ] 场景卡片式编辑器
- [ ] Word 剧本文档导出

### 中期计划（v3.0）
- [ ] 多版本差异对比
- [ ] 对白润色功能
- [ ] 目标时长压缩算法
- [ ] 分镜脚本生成

### 长期愿景
- [ ] 云端协作（多人实时编辑）
- [ ] AI 导演建议（镜头、配乐）
- [ ] 自动生成分镜图
- [ ] 接入视频生成 API

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- Python：遵循 PEP 8
- TypeScript：使用 ESLint 配置
- 提交信息：遵循 Conventional Commits

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

**声明**：
- ✅ 本项目仅供学习、比赛和原型评审使用
- ⚠️ 使用 AI 模式前请确认内容授权和隐私合规
- 🔒 不要提交包含真实 API Key 的代码

---

## 👥 团队信息

<!-- 根据实际情况填写 -->
```
📸 截图位置（可选）：团队成员照片或组织架构图
```

**开发团队**：[填写你的团队名称或成员]

**指导老师**：[如果有，填写导师信息]

**比赛信息**：[填写参赛的比赛名称]

---

## 📞 联系方式

- 📧 邮箱：[your-email@example.com]
- 🌐 项目主页：[项目链接]
- 💬 问题反馈：[Issue Tracker 链接]

---

<div align="center">

### ⭐ 如果这个项目对你有帮助，请给我们一个 Star！

**Novel2Script** - 让每一个故事都能成为精彩剧本 🎬

Made with ❤️ by [Your Team Name]

</div>
