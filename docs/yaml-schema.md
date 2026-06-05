# 剧本 YAML Schema 设计文档

## 1. 文档目的

本文档定义 Novel2Script 生成剧本时使用的 YAML Schema，并说明该 Schema 的设计原因。该 Schema 用于约束 AI 生成内容，使小说改编后的剧本初稿具备稳定结构，方便作者编辑、系统校验和后续导出。

本 Schema 面向 MVP 阶段，重点支持以下目标：

- 将 3 个章节以上的小说文本转换为结构化剧本。
- 保留小说章节与剧本场景之间的来源关系。
- 统一管理角色、场景、对白、动作和改编说明。
- 让 AI 输出结果可以被程序校验。
- 让作者可以直接阅读和修改 YAML 文件。

## 2. 设计原则

### 2.1 以场景为核心

剧本创作通常以场景为基本组织单位，因此 Schema 使用 `scenes` 作为剧本主体。每个场景包含地点、时间、出场角色、剧情目的和具体内容片段。

这样设计的原因是：

- 场景结构符合影视、短剧和广播剧创作习惯。
- 场景天然适合前端卡片式编辑和后续导出。
- 场景可以与小说章节建立映射，方便作者追溯原文来源。

### 2.2 角色独立管理

Schema 将角色信息放入独立的 `characters` 列表中，而不是在每个场景中重复描述角色。

这样设计的原因是：

- 避免同一角色在不同场景中名称不一致。
- 方便维护角色身份、性格、关系和首次出场章节。
- 后端可以校验场景中引用的角色是否存在。
- 后续可以扩展角色关系图和人物卡片。

### 2.3 使用 ID 引用

章节、角色和场景都使用稳定 ID：

- 章节 ID：`C001`
- 角色 ID：`CHAR001`
- 场景 ID：`S001`

这样设计的原因是：

- 名称可能重复或变化，ID 更适合程序处理。
- 可以做跨字段引用校验。
- 方便后续支持排序、编辑、导出和版本对比。

### 2.4 使用 beats 表示场景内容

每个场景中的具体剧本内容使用 `beats` 表示。一个 beat 是场景内的最小内容单元，可以是动作、对白、旁白、转场或备注。

支持的类型包括：

- `action`：人物动作或场景动作
- `dialogue`：人物对白
- `narration`：旁白或画外音
- `transition`：转场提示
- `note`：创作备注

这样设计的原因是：

- 比单纯的长文本更容易编辑和校验。
- 可以区分动作、对白和旁白等不同剧本元素。
- 便于后续扩展分镜、音效、音乐和镜头信息。
- 前端可以按类型展示不同样式。

### 2.5 保留改编说明

Schema 提供 `adaptation_notes` 字段，用于记录 AI 在改编过程中进行的删减、合并、转化或新增。

这样设计的原因是：

- 提高 AI 改编结果的可解释性。
- 帮助作者判断 AI 是否误删关键剧情。
- 方便答辩时说明系统不是简单改写，而是有结构化改编过程。

### 2.6 保留待确认问题

Schema 提供 `open_questions` 字段，用于记录 AI 无法确定的信息，例如人物关系、时间线、隐藏动机或原文歧义。

这样设计的原因是：

- 避免 AI 强行编造不确定内容。
- 提醒作者后续人工确认。
- 提升剧本初稿的可用性和可信度。

## 3. 顶层结构

完整 YAML 文件必须包含 `script` 顶层字段。

```yaml
script:
  title: string
  genre: string
  version: string
  created_at: string
  source:
    chapter_count: number
    chapters: []
  characters: []
  scenes: []
  adaptation_notes: []
  open_questions: []
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `title` | string | 是 | 剧本标题 |
| `genre` | string | 是 | 剧本类型，例如都市、悬疑、古装 |
| `version` | string | 是 | 剧本版本号 |
| `created_at` | string | 否 | 生成时间，建议使用 ISO 8601 格式 |
| `source` | object | 是 | 小说来源信息 |
| `characters` | array | 是 | 角色表 |
| `scenes` | array | 是 | 剧本场景列表 |
| `adaptation_notes` | array | 是 | 改编说明 |
| `open_questions` | array | 是 | 待确认问题 |

## 4. source 结构

`source` 用于描述原小说章节信息。

```yaml
source:
  chapter_count: 3
  chapters:
    - id: C001
      title: 第一章 雨夜来客
      word_count: 3200
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `chapter_count` | number | 是 | 原小说章节数量 |
| `chapters` | array | 是 | 章节列表 |
| `chapters[].id` | string | 是 | 章节 ID，格式为 `C001` |
| `chapters[].title` | string | 是 | 章节标题 |
| `chapters[].word_count` | number | 否 | 章节字数 |

### 设计原因

保留章节来源有两个作用。第一，作者可以知道每个剧本场景来自原小说的哪一章。第二，系统可以校验 `source_chapters` 是否引用了真实存在的章节。

## 5. characters 结构

`characters` 用于统一管理剧本中的角色。

```yaml
characters:
  - id: CHAR001
    name: 林昭
    role: 主角
    description: 年轻捕快，冷静敏锐，背负旧案秘密。
    personality:
      - 冷静
      - 敏锐
    first_appearance: C001
    aliases:
      - 林捕快
    relationships:
      - character_id: CHAR002
        relation: 互相试探的合作对象
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 角色 ID，格式为 `CHAR001` |
| `name` | string | 是 | 角色姓名 |
| `role` | string | 是 | 角色定位，例如主角、配角、反派 |
| `description` | string | 否 | 人物简介 |
| `personality` | array | 否 | 性格特征列表 |
| `first_appearance` | string | 是 | 首次出场章节 ID |
| `aliases` | array | 否 | 角色别称 |
| `relationships` | array | 否 | 与其他角色的关系 |

### 设计原因

小说中同一人物可能有姓名、称呼、身份称谓等不同表达。通过角色表统一角色，可以减少 AI 在剧本中混用名称的问题。`aliases` 字段用于保存别称，但剧本场景内统一引用角色 ID。

## 6. scenes 结构

`scenes` 是剧本主体，每个场景表示一段可独立理解和编辑的剧情。

```yaml
scenes:
  - id: S001
    title: 雨夜客栈
    source_chapters:
      - C001
    location: 城南客栈
    time: 夜晚
    characters:
      - CHAR001
      - CHAR002
    purpose: 引出主角相遇，并埋下旧案线索。
    beats: []
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `id` | string | 是 | 场景 ID，格式为 `S001` |
| `title` | string | 是 | 场景标题 |
| `source_chapters` | array | 是 | 来源章节 ID 列表 |
| `location` | string | 是 | 场景地点 |
| `time` | string | 是 | 场景时间 |
| `characters` | array | 是 | 出场角色 ID 列表 |
| `purpose` | string | 是 | 场景的剧情作用 |
| `beats` | array | 是 | 场景内容，至少 3 个 beat |

### 设计原因

场景中的 `purpose` 字段不是传统剧本必需内容，但对 AI 生成和作者修改很有帮助。它能说明该场景为什么存在，例如建立人物关系、推进冲突、揭示线索或制造悬念。

## 7. beats 结构

`beats` 是场景内容的最小结构单元。

```yaml
beats:
  - type: action
    text: 林昭推门而入，雨水顺着衣角滴落。
  - type: dialogue
    character: CHAR002
    text: 你终于来了。
    emotion: 克制
  - type: transition
    text: 切至客栈外的雨夜长街。
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `type` | string | 是 | beat 类型 |
| `text` | string | 是 | 内容文本 |
| `character` | string | 条件必填 | 当 `type` 为 `dialogue` 时必填 |
| `emotion` | string | 否 | 对白情绪 |
| `notes` | string | 否 | 创作备注 |

### 类型约束

`type` 只能使用以下值：

- `action`
- `dialogue`
- `narration`
- `transition`
- `note`

### 设计原因

小说中的心理描写和环境描写需要转化为适合剧本呈现的内容。`beats` 可以将这些内容拆分为动作、对白和旁白，使结果更接近剧本初稿，而不是普通文章改写。

## 8. adaptation_notes 结构

`adaptation_notes` 用于记录 AI 的改编行为。

```yaml
adaptation_notes:
  - type: transformation
    description: 将第一章中林昭的心理活动转化为与沈月的对白。
    reason: 剧本需要通过可听见、可看见的内容表现人物状态。
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `type` | string | 是 | 改编类型 |
| `description` | string | 是 | 改编内容说明 |
| `reason` | string | 是 | 改编原因 |

### 类型约束

`type` 只能使用以下值：

- `deletion`：删减
- `merge`：合并
- `transformation`：转化
- `addition`：新增

## 9. open_questions 结构

`open_questions` 用于记录待作者确认的问题。

```yaml
open_questions:
  - question: 沈月是否知道旧案真相？
    context: 原文只通过眼神和停顿暗示，未明确说明。
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `question` | string | 是 | 待确认问题 |
| `context` | string | 否 | 问题相关上下文 |

## 10. 校验规则

后端应至少实现以下校验规则：

- `script` 顶层字段必须存在。
- `title`、`genre`、`version`、`source`、`characters`、`scenes` 必须存在。
- `source.chapter_count` 必须大于等于 3。
- `source.chapters[].id` 必须唯一。
- `characters[].id` 必须唯一。
- `scenes[].id` 必须唯一。
- `characters[].first_appearance` 必须引用已存在的章节 ID。
- `scenes[].source_chapters` 必须引用已存在的章节 ID。
- `scenes[].characters` 必须引用已存在的角色 ID。
- `scenes[].beats` 至少包含 3 个 beat。
- 当 beat 的 `type` 为 `dialogue` 时，`character` 必须存在。
- dialogue beat 的 `character` 必须引用已存在的角色 ID。
- `adaptation_notes[].type` 必须是允许值。

## 11. 标准示例

标准 YAML 示例文件位于：

```text
examples/script-output-1.yaml
```

机器可校验的 JSON Schema 文件位于：

```text
schemas/script.schema.json
```

## 12. 后续扩展

该 Schema 后续可扩展以下字段：

- `shot`：镜头信息
- `sound_effect`：音效
- `music`：音乐提示
- `duration_estimate`：预计时长
- `episode`：集数信息
- `revision_history`：版本历史
- `export_profiles`：不同导出格式设置

这些字段暂不纳入 MVP，避免第一阶段实现过重。

