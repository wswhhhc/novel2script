# 测试指南

## 运行方式速查

```bash
# ── 后端 ──
source venv/bin/activate

# 全部后端测试
python -m pytest backend/tests/ -v

# 单个文件
python -m pytest backend/tests/test_chapter_parser.py -v

# 单个测试
python -m pytest backend/tests/test_script_validator.py::test_sample_yaml_passes_validation -v

# 含覆盖率
python -m pytest backend/tests/ --cov=app --cov-report=term-missing

# ── 前端 ──
cd frontend

# 全部
npx vitest run

# 持续运行
npx vitest

# 单个文件
npx vitest run src/api/__tests__/client.test.ts

# 单个测试
npx vitest run -t "parses NDJSON events"

# 静态 smoke test
npm run smoke

# ── 端到端 ──
# 确保后端运行在 8000 端口
npm run e2e                    # Playwright E2E
```

---

## 1. 单元测试（Unit Tests）

单元测试验证**最小可测试单元**（函数、方法、类）在隔离环境中的行为。外部依赖（网络、数据库、文件系统）全部通过 mock 或桩件替代。

### 后端单元测试

| 文件 | 测试数 | 被测单元 | 隔离方式 |
|------|--------|----------|----------|
| `test_chapter_parser.py` | 4 | `chapter_parser.parse_chapters()` | 纯函数，无外部依赖 |
| `test_script_validator.py` | 5 | `script_validator.validate_script()` | JSON Schema 本地加载 |
| `test_ai_client.py` | 5 | `parse_json_response()`、配置检查 | 无网络调用 |
| `test_prompt_loader.py` | 3 | `prompt_loader` 模板替换 | 本地文件读取 |
| `test_script_generator_ai.py` | 2 | `_extract_yaml_from_response()`、缓存读写 | 纯函数 + 临时目录 |

**关键测试示例**：

```python
# test_chapter_parser.py — 纯函数测试，无 mock
def test_standard_format(client):
    result = parse_chapters("第一章 相遇\n正文内容\n第二章 发展\n更多内容")
    assert result.chapter_count == 2
    assert result.valid is True

# test_ai_client.py — JSON 解析测试
def test_parse_json_from_code_block():
    text = "```json\n{\"key\": \"value\"}\n```"
    assert parse_json_response(text) == {"key": "value"}
```

### 前端单元测试

| 文件 | 测试数 | 被测单元 | 隔离方式 |
|------|--------|----------|----------|
| `src/api/__tests__/client.test.ts` | 24 | `request()`、`extractErrorMessage()`、`consumeNdjsonBuffer()`、`parseStreamEvent()` 等工具函数 | fetch 全局 mock |
| `src/components/__tests__/ValidationPanel.test.tsx` | 7 | `ValidationPanel` 组件四种状态渲染 | Mock Monaco Editor |

**关键测试示例**：

```typescript
// 工具函数测试 — request() 错误提取
it("extracts error from string body", async () => {
  mockFetch.mockResolvedValueOnce(
    new Response("Service unavailable", { status: 503, headers: { "content-type": "text/plain" } })
  );
  await expect(client.checkHealth()).rejects.toThrow("Service unavailable");
});

// 工具函数测试 — NDJSON 流式解析
it("parses NDJSON events", async () => {
  const ndjson = [
    JSON.stringify({ type: "status", message: "start" }),
    JSON.stringify({ type: "done", yaml: "output", validation: { valid: true, errors: [] } }),
  ].join("\n");
  // ... mock stream response, assert onEvent called 2 times
});
```

---

## 2. 集成测试（Integration Tests）

集成测试验证**多个单元协同工作**，但仍在受控环境中运行（使用测试数据库、模拟 AI 调用）。

### 后端集成测试

| 文件 | 测试数 | 集成范围 |
|------|--------|----------|
| `test_script_generator_ai.py` | 4 | AI 五阶段管线 + YAML 修复循环 + 缓存集成 |
| `test_sample_inputs.py` | 3 | 解析 → 生成 → 校验 全流程（使用 `examples/` 真实数据） |
| `test_advanced_scenarios.py` | 6 | 部分 AI 阶段失败、畸形 JSON、超长章节裁剪、重试耗尽、循环引用 |
| `test_limits.py` | 5 | 章节数/字数边界值（接近上限、超过上限、最大章节数） |

**测试环境隔离**：
- `conftest.py` 创建独立的 SQLite `:memory:` 数据库
- AI 调用通过 `monkeypatch` 模拟，默认禁用网络请求
- 每个测试函数使用独立的 TestClient 实例

**关键测试示例**：

```python
# test_script_generator_ai.py — 模拟 AI 五阶段管线
def test_generate_script_with_ai_runs_all_generation_stages(monkeypatch):
    stages_called = []
    def mock_ai(prompt):
        stages_called.append(detect_stage(prompt))
        return mock_stage_response(prompt)

    monkeypatch.setattr("app.services.script_generator.call_ai_model", mock_ai)
    result = generate_script_with_ai("测试", "悬疑", chapters)
    assert len(stages_called) == 5  # 5 stages all called
    assert result.validation.valid is True

# test_limits.py — 边界值测试
def test_max_chapters(client):
    """20 章应该能正常通过。"""
    content = "\n\n".join(f"第{i}章 标题" for i in range(1, 21))
    response = client.post("/api/chapters/parse", json={"content": content})
    assert response.status_code == 200
    assert response.json()["chapter_count"] == 20
```

### 前端集成测试

| 文件 | 测试数 | 集成范围 |
|------|--------|----------|
| `src/components/__tests__/NovelInput.test.tsx` | 5 | 输入组件 + 文件上传 + 字数统计 |
| `src/components/__tests__/YamlEditor.test.tsx` | 8 | 编辑器 + 复制/下载/校验按钮 + ValidationPanel 联动 |

**关键测试示例**：

```typescript
// NovelInput 集成测试 — 填写标题和内容后触发解析
it("handles title input and content typing", async () => {
  const onTitleChange = vi.fn();
  render(<NovelInput title="" genre="悬疑" content="" onTitleChange={onTitleChange} ... />);
  await user.type(screen.getByLabelText("小说标题"), "我的小说");
  expect(onTitleChange).toHaveBeenLastCalledWith("我的小说");
});
```

---

## 3. 接口测试（API Tests）

接口测试直接验证 HTTP API 端点（路由 → 请求模型 → 业务逻辑 → 响应模型 全链路）。

### 后端接口测试

| 文件 | 测试数 | 覆盖端点 |
|------|--------|----------|
| `test_api.py` | 7 | `GET /health`、`POST /api/chapters/parse`、`POST /api/script/validate`、`POST /api/script/generate`、`POST /api/script/generate/stream`、`GET /api/script/mode` |
| `test_projects_api.py` | 12 | `GET/POST /api/projects`、`GET/PUT/DELETE /api/projects/{id}`、`GET/POST /api/projects/{id}/versions`、`GET /api/projects/{id}/versions/{id}`、`POST /api/projects/{id}/versions/{id}/restore`、`GET /api/projects/{id}/export/{format}` |
| `test_batch_api.py` | 5 | `POST /api/batch/delete`、`POST /api/batch/validate`、`GET /api/batch/stats` |

**测试约定**：
- 使用 FastAPI TestClient（基于 httpx）
- 传递完整请求体验证请求模型校验
- 验证 HTTP 状态码 + 响应体结构 + 关键字段值
- 覆盖 200、201、404、422、405 等状态码

**关键测试示例**：

```python
# test_api.py — 流式生成接口
def test_generate_stream_returns_ndjson(client):
    response = client.post(
        "/api/script/generate/stream",
        json={"title": "测试", "genre": "都市", "chapters": chapters},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/x-ndjson"
    events = [json.loads(line) for line in response.text.strip().split("\n")]
    assert events[0]["type"] == "status"
    assert events[-1]["type"] == "done"

# test_projects_api.py — 项目导出
def test_export_markdown_contains_title_characters_and_scenes(client):
    project = create_test_project(client)
    response = client.get(f"/api/projects/{project['id']}/export/markdown")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/markdown"
    assert "测试" in response.text
    assert "角色" in response.text

# test_batch_api.py — 批量操作
def test_batch_delete_removes_projects(client):
    ids = [create_test_project(client)["id"] for _ in range(3)]
    response = client.post("/api/batch/delete", json={"project_ids": ids})
    assert response.status_code == 200
    assert response.json()["deleted_count"] == 3
```

---

## 4. 冒烟测试（Smoke Tests）

冒烟测试验证系统**核心功能是否可用**，通常在部署后或大变更后运行。

### 静态冒烟测试（前端）

```bash
npm run smoke
```

`frontend/scripts/smoke-test.mjs` 执行内容：
1. 验证构建产物存在（`dist/index.html`、`dist/assets/*.js`、`dist/assets/*.css`）
2. 验证 HTML 包含正确标题和入口标签
3. 验证 JS 和 CSS 文件可读

### 手动冒烟测试清单

部署后应验证以下核心路径：

| 步骤 | 预期结果 |
|------|----------|
| 打开前端页面 `http://<host>/novel2/` | 页面加载，无白屏/JS 错误 |
| 填写标题和小说正文 | 字数统计更新 |
| 点击"识别章节" | 章节列表出现，无报错 |
| 点击"生成剧本" | 流式输出 YAML，进度条推进 |
| 点击"校验" | 校验通过/失败清晰显示 |
| 保存项目→创建版本→恢复版本 | 数据完整 |
| 导出 YAML/JSON/Markdown | 文件下载，内容正确 |

---

## 5. 系统功能测试（System / Functional Tests）

系统功能测试从**用户视角**验证完整业务流程。

### 核心业务路径

**路径 1：创作流程**
```
输入小说 → 识别章节 → 生成剧本 → 校验 → 保存 → 导出
```

**路径 2：项目管理**
```
新建项目 → 保存 → 创建版本快照 → 修改 → 恢复版本 → 导出
```

**路径 3：并行处理**
```
同时打开多个项目 → 切换编辑 → 各自保存
```

### AI 模式测试

| 场景 | 验证点 |
|------|--------|
| Mock 模式（`ENABLE_AI_GENERATION=false`） | 返回示例 YAML，无需 API Key |
| AI 模式（`ENABLE_AI_GENERATION=true`） | 五阶段生成，含角色/场景/对白 |
| AI 自动修复 | 生成不合法的 YAML → 3 次自动修复尝试 |
| API Key 缺失 | 返回清晰错误，提示配置 |
| 网络超时 | 自动重试（可配置次数） |
| 熔断触发 | 连续 5 次失败 → 暂停 60 秒 → 自动恢复 |

---

## 6. 回归测试（Regression Tests）

回归测试确保**新代码不破坏已有功能**。当前回归测试覆盖：

### 高级场景（`test_advanced_scenarios.py` — 6 个测试）

| 测试 | 回归范围 |
|------|----------|
| 部分 AI 阶段失败 | 阶段 2 失败 → 后续阶段正常执行 |
| 畸形 AI 响应 | 返回无法解析的 JSON → 清晰报错 |
| 超长章节裁剪 | 章节 >8000 字 → 取首尾各 4000 字 + 裁剪标记 |
| 重试上限耗尽 | 持续失败 → 返回部分结果 + 错误信息 |
| 循环引用 | 角色关系互相引用 → 校验拒绝 |
| 缺失配置 | API Key 未设置 → 返回 Mock 模式 | 

### 边界和极限条件（`test_limits.py` — 5 个测试）

| 测试 | 边界值 |
|------|--------|
| 章节数低于下限 | 2 章 → 校验拒绝 |
| 章节数等于下限 | 3 章 → 正常 |
| 章节数等于上限 | 20 章 → 正常 |
| 章节数超过上限 | 21 章 → 校验拒绝 |
| 输入总字数超过限制 | 50001 字 → 校验拒绝 |

### 示例文件回归（`test_sample_inputs.py` — 3 个测试）

每次修改 Schema 或校验逻辑后，运行：
```bash
python -m pytest backend/tests/test_sample_inputs.py -v
```

确保 `examples/` 目录中的示例文件仍然解析和校验正确。

---

## 测试覆盖率总览

```
全部测试: 115 个
├── 后端: 68 个（12 个文件）
│   ├── 单元测试:     19 个
│   ├── 集成测试:     18 个
│   ├── 接口测试:     24 个
│   └── 回归测试:     17 个
│
├── 前端: 47 个（4 个文件）
│   ├── 单元测试:     24 个（API client 工具函数）
│   ├── 组件测试:      5 个（NovelInput）
│   └── 组件测试:     15 个（YamlEditor + ValidationPanel）
│
└── 端到端:  0 个（Playwright 已配置，待补充测试用例）
```

---

## 测试金字塔

```
        ╱╲
       ╱  ╲               E2E / 手动冒烟
      ╱    ╲
     ╱ API  ╲             接口测试（24 个）
    ╱  Tests  ╲
   ╱────────────╲
  ╱  集成测试     ╲       集成测试（18 个）
 ╱────────────────╲
╱   单元测试        ╲     单元测试（43 个）
╱────────────────────╲
```

---

## 待补充的测试

| 类型 | 内容 | 优先级 |
|------|------|--------|
| Hooks 测试 | `useWorkspace`、`useProjects` 独立测试 | 高 |
| App 集成测试 | 全组件联动测试 | 高 |
| E2E 测试 | Playwright 浏览器自动化测试 | 中 |
| 性能测试 | 大文件（50K 字）解析+生成 | 低 |
| 安全测试 | SQL 注入、XSS、CSRF | 低 |
| Snapshot 测试 | UI 渲染一致性 | 低 |
