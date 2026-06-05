# 配音脚本使用指南

本目录包含 8 个分段的配音脚本文件，可用于生成 AI 配音。

---

## 📁 脚本文件列表

```
voice-scripts/
├── 01-opening.txt              开场介绍（30秒）
├── 02-chapter-recognition.txt  章节识别演示（30秒）
├── 03-ai-generation.txt        AI 生成演示（1分钟）
├── 04-yaml-editor.txt          YAML 编辑器（30秒）
├── 05-project-management.txt   项目管理（30秒）
├── 06-export.txt               导出功能（30秒）
├── 07-highlights.txt           技术亮点（30秒）
└── 08-ending.txt               结尾总结（30秒）
```

**总时长**：约 3-4 分钟（配合操作演示）

---

## 🎙️ 使用方法

### 方案 1：剪映（推荐）⭐

**步骤**：
```
1. 打开剪映 PC 版
2. 新建项目
3. 点击"文本" → "新建文本"
4. 打开 01-opening.txt，复制内容，粘贴到文本框
5. 选择文本 → "文字朗读"
6. 选择声音：
   - 女声推荐："温柔女声-知性"
   - 男声推荐："磁性男声-浑厚"
7. 语速：1.0x 或 1.1x
8. 点击"应用"，生成配音
9. 重复步骤 3-8，生成所有 8 段配音
10. 导出音频文件（MP3 或 WAV）
```

**导出音频**：
```
1. 选中时间线上的音频
2. 右键 → "导出音频"
3. 文件命名：01-opening.mp3, 02-chapter.mp3, ...
4. 保存到本地
```

---

### 方案 2：Azure Text-to-Speech（专业）⭐⭐

**在线工具**：https://speech.microsoft.com/portal/voicegallery

**步骤**：
```
1. 访问 Azure 语音库
2. 选择声音：
   - zh-CN-XiaoxiaoNeural（云希，女声）
   - zh-CN-YunyangNeural（云扬，男声）
3. 依次复制每个脚本文件内容
4. 点击"试听"
5. 满意后点击"下载"
6. 保存为 MP3 文件
```

**批量生成**（需要 API Key）：
```python
# 安装：pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk
import os

speech_key = "YOUR_API_KEY"
service_region = "eastasia"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "zh-CN-XiaoxiaoNeural"

# 批量生成
scripts_dir = "docs/voice-scripts"
output_dir = "docs/voice-output"
os.makedirs(output_dir, exist_ok=True)

for i in range(1, 9):
    script_file = f"{scripts_dir}/{i:02d}-*.txt"
    output_file = f"{output_dir}/{i:02d}.mp3"
    
    with open(script_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = synthesizer.speak_text_async(text).get()
    print(f"Generated: {output_file}")
```

---

### 方案 3：讯飞配音（在线）

**网址**：https://peiyin.xunfei.cn/

**步骤**：
```
1. 访问讯飞配音
2. 选择声音（推荐：许久、小燕）
3. 依次复制每个脚本文件内容
4. 点击"合成"
5. 下载 MP3 文件
```

---

## 📹 配合视频录制

### 工作流程

**先配音，后录制**（推荐）：
```
1. ✅ 使用上述方法生成 8 段配音音频
2. ✅ 保存为 MP3 文件（01.mp3, 02.mp3, ...）
3. ✅ 播放配音，同时录制屏幕操作
4. ✅ 在剪映中合成音频和视频
```

**具体步骤**：
```
第 1 步：生成所有配音
- 使用剪映或 Azure TTS
- 导出 8 个 MP3 文件

第 2 步：播放配音并录制
- 使用任意音频播放器播放配音
- 听着配音同步操作演示
- 使用 OBS 或 Win+G 录制屏幕
- 操作节奏跟随配音

第 3 步：后期合成
- 在剪映中导入录制的视频
- 导入配音 MP3 文件
- 对齐音画
- 导出最终视频
```

---

## 🎯 配音建议

### 语速设置
- **正常语速**：1.0x（推荐）
- **稍快**：1.1x
- **稍慢**：0.9x

### 停顿设置
- 句号：停顿 0.5 秒
- 逗号：停顿 0.3 秒
- 分号：停顿 0.4 秒

### 音调建议
- **开场和结尾**：稍微激昂，充满热情
- **功能演示**：平稳、清晰、专业
- **技术亮点**：强调关键词汇

### 强调词汇
在以下词汇处可以稍作停顿或加重语气：
- 核心概念：五阶段、Schema、版本控制
- 技术栈：FastAPI、React、TypeScript
- 特色功能：自动识别、自动修复、实时校验

---

## 📊 脚本统计

| 文件 | 内容 | 字数 | 预计时长 |
|------|------|------|---------|
| 01-opening.txt | 开场介绍 | 90 字 | 30 秒 |
| 02-chapter-recognition.txt | 章节识别 | 110 字 | 30 秒 |
| 03-ai-generation.txt | AI 生成 | 220 字 | 60 秒 |
| 04-yaml-editor.txt | YAML 编辑 | 95 字 | 30 秒 |
| 05-project-management.txt | 项目管理 | 115 字 | 30 秒 |
| 06-export.txt | 导出功能 | 85 字 | 30 秒 |
| 07-highlights.txt | 技术亮点 | 95 字 | 30 秒 |
| 08-ending.txt | 结尾总结 | 75 字 | 30 秒 |
| **总计** | - | **885 字** | **4 分钟** |

---

## ✅ 质量检查

### 配音后检查
- [ ] 发音清晰准确
- [ ] 语速适中（每分钟 200-220 字）
- [ ] 停顿自然
- [ ] 音量一致
- [ ] 无杂音

### 合成后检查
- [ ] 音画同步
- [ ] 操作和配音内容匹配
- [ ] 音量适中，不盖过系统声音
- [ ] 总时长 3-5 分钟

---

## 🚀 快速开始

**最快生成配音的方法**：

```
1. 下载剪映 PC 版
2. 新建项目
3. 依次打开 8 个脚本文件
4. 逐个生成配音
5. 导出音频文件
6. 播放配音，同步录制操作
7. 在剪映中合成
8. 导出视频
```

**预计时间**：30-60 分钟

---

## 💡 提示

- 所有脚本已优化为适合 AI 配音的节奏和断句
- 可以根据实际需要调整脚本内容
- 建议先试听一小段，确认声音效果后再批量生成
- 配音文件建议保存备份

---

**开始生成你的配音吧！** 🎙️✨
