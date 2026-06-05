# 第四阶段测试报告

## 测试范围

本阶段围绕 MVP 主流程和需求文档 TC001-TC010 做测试补全：

- 示例小说输入和边界 fixture。
- 后端章节解析、输入限制、Mock 生成、YAML 校验。
- 前端关键状态 smoke test。
- 前后端主流程：解析章节 -> 生成 YAML -> 校验 YAML。

## 自动化测试命令

```bash
python -m pytest backend/tests
cd frontend
npm run smoke
npm run build
```

本次验证结果：

```text
backend: 32 passed
frontend smoke: passed
frontend build: passed
```

## 覆盖的 TC

| TC | 覆盖方式 | 说明 |
| --- | --- | --- |
| TC001 标准 3 章节小说 | 自动化 | `examples/novel-sample-1.txt` 解析、Mock 生成、YAML 校验 |
| TC002 章节不足 | 自动化 | `examples/novel-edge-too-few-chapters.txt` 返回 invalid 和明确 message；前端 smoke 检查生成按钮禁用逻辑 |
| TC003 无法识别章节 | 自动化 | 无章节标题文本返回 invalid 和明确 message |
| TC004 超长章节 | 自动化 | 单章超过 10,000 字返回 warning，仍允许 Mock 生成 |
| TC005 多种章节格式混合 | 自动化 | 覆盖“第一章”“Chapter 2”“3.”“卷一 第四章”，ID 从 C001 递增 |
| TC006 角色名称一致性 | fixture/文档化 | `examples/script-output-1.yaml` 校验角色 ID、aliases、relationships 结构 |
| TC007 YAML 校验失败 | 自动化 | `invalid-script-missing-required.yaml` 和 `invalid-script-bad-reference.yaml` 返回 readable errors；前端 smoke 检查错误列表和编辑保留 |
| TC008 输入边界 | 自动化 | 接近 50,000 字、20 章输入可处理 |
| TC009 超出限制 | 自动化 | 超 50,000 字和超过 20 章被拒绝并返回明确提示 |
| TC010 复杂人物关系 | fixture/文档化 | 当前用标准 YAML 的 relationships 结构验证；复杂质量需真实 AI 阶段人工评估 |

## 已新增示例数据

- `examples/novel-sample-1.txt`：都市类型 3 章，主流程演示。
- `examples/novel-sample-2.txt`：悬疑类型 5 章。
- `examples/novel-sample-3.txt`：古装武侠类型 4 章。
- `examples/novel-edge-too-few-chapters.txt`：2 章边界。
- `examples/novel-edge-mixed-chapter-formats.txt`：混合章节标题格式。
- `examples/invalid-script-missing-required.yaml`：缺少必填字段。
- `examples/invalid-script-bad-reference.yaml`：角色和章节引用错误。

## 已发现并修复的问题

- 解析结果存在 warnings 时，前端顶部状态原先仍显示成功态；已改为 warning 态。
- 上传新文件、修改正文、清空输入时旧 YAML 和旧校验状态可能残留；已清理旧输出，避免误导演示。
- 缺少可执行前端 smoke test；已新增 `frontend/scripts/smoke-test.mjs` 和 `npm run smoke`。

## 当前限制与后续建议

- MVP 默认 Mock 生成，不评估真实 AI 改编质量。
- TC006 和 TC010 的内容质量需要在启用真实 AI 后加入人工验收或更强 fixture。
- 前端 smoke test 当前是轻量静态检查；后续可引入 Playwright 覆盖真实浏览器点击流程。
- 章节解析暂未实现 AI 智能识别和用户手动标注，无法识别纯标题或弱格式文本时会返回明确错误。
