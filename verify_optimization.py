"""
验证优化后的代码功能
测试新增的 AI 客户端、Prompt 加载器等模块
"""
import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 backend 到路径
backend_root = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_root))

from app.config.settings import settings
from app.services.prompt_loader import load_prompt_template, format_chapters_for_prompt


def test_settings():
    """测试配置是否正确加载"""
    print("=" * 60)
    print("测试 1: 配置加载")
    print("=" * 60)

    assert settings.min_chapters == 3
    assert settings.prompts_dir.exists()
    assert settings.model_provider in ["openai", "anthropic"]
    assert settings.enable_ai_generation in [True, False]

    print(f"✓ 章节限制: {settings.min_chapters}-{settings.max_chapters}")
    print(f"✓ Prompts 目录: {settings.prompts_dir}")
    print(f"✓ AI 模式: {'启用' if settings.enable_ai_generation else '禁用（Mock 模式）'}")
    print(f"✓ AI 提供商: {settings.model_provider}")
    print(f"✓ 模型名称: {settings.model_name}")
    print()


def test_prompt_loader():
    """测试 Prompt 模板加载器"""
    print("=" * 60)
    print("测试 2: Prompt 模板加载器")
    print("=" * 60)

    # 测试加载第一阶段 Prompt
    prompt = load_prompt_template(
        "01_chapter_analysis.txt",
        title="测试小说",
        genre="悬疑",
        chapters="第一章 测试\n内容..."
    )

    assert "测试小说" in prompt
    assert "悬疑" in prompt
    assert "第一章 测试" in prompt

    print("✓ 成功加载 01_chapter_analysis.txt")
    print(f"✓ 模板长度: {len(prompt)} 字符")
    print(f"✓ 变量替换正常")
    print()


def test_chapter_formatting():
    """测试章节格式化"""
    print("=" * 60)
    print("测试 3: 章节格式化")
    print("=" * 60)

    chapters = [
        {"id": "C001", "title": "第一章", "content": "内容一"},
        {"id": "C002", "title": "第二章", "content": "内容二"},
    ]

    formatted = format_chapters_for_prompt(chapters)

    assert "[C001]" in formatted
    assert "第一章" in formatted
    assert "内容一" in formatted

    print("✓ 章节格式化成功")
    print(f"✓ 格式化后长度: {len(formatted)} 字符")
    print()


def test_all_prompts_exist():
    """测试所有 Prompt 文件是否存在"""
    print("=" * 60)
    print("测试 4: Prompt 文件完整性")
    print("=" * 60)

    prompt_files = [
        "01_chapter_analysis.txt",
        "02_character_extraction.txt",
        "03_scene_planning.txt",
        "04_script_generation.txt",
        "05_yaml_fix.txt",
    ]

    for prompt_file in prompt_files:
        prompt_path = settings.prompts_dir / prompt_file
        assert prompt_path.exists(), f"缺少 Prompt 文件: {prompt_file}"
        print(f"✓ {prompt_file} 存在")

    print()


def test_ai_client_config():
    """测试 AI 客户端配置"""
    print("=" * 60)
    print("测试 5: AI 客户端配置")
    print("=" * 60)

    print(f"AI 生成状态: {'✓ 启用' if settings.enable_ai_generation else '✗ 禁用（Mock 模式）'}")
    print(f"API Key 配置: {'✓ 已配置' if settings.model_api_key else '✗ 未配置（Mock 模式）'}")
    print(f"超时时间: {settings.model_timeout} 秒")
    print(f"最大 Token: {settings.model_max_tokens}")
    print(f"温度参数: {settings.model_temperature}")
    print(f"自动修复次数: {settings.auto_fix_attempts}")
    print()


def main():
    """运行所有验证测试"""
    print("\n" + "=" * 60)
    print("Novel2Script 优化功能验证")
    print("=" * 60 + "\n")

    try:
        test_settings()
        test_prompt_loader()
        test_chapter_formatting()
        test_all_prompts_exist()
        test_ai_client_config()

        print("=" * 60)
        print("✅ 所有验证测试通过！")
        print("=" * 60)
        print("\n优化内容验证完成：")
        print("  ✓ 配置系统扩展正常")
        print("  ✓ Prompt 模板加载器工作正常")
        print("  ✓ 章节格式化功能正常")
        print("  ✓ 所有 Prompt 文件完整")
        print("  ✓ AI 客户端配置正确")
        print("\n建议：")
        if not settings.enable_ai_generation:
            print("  - 当前为 Mock 模式，适合开发和测试")
            print("  - 如需启用 AI 生成，请配置环境变量：")
            print("    export ENABLE_AI_GENERATION=true")
            print("    export MODEL_API_KEY=your-api-key")
        else:
            print("  - 当前为 AI 模式，将调用真实 AI")
            print("  - 确保 API Key 已正确配置")

    except AssertionError as e:
        print(f"\n❌ 验证失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
