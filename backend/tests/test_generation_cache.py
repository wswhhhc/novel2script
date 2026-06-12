"""
测试生成缓存服务
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.services.generation_cache import get_cached_stage, set_cached_stage


def test_cache_miss_returns_none():
    """未命中缓存返回 None"""
    result = get_cached_stage("chapter_analysis", "prompt that was never cached before")
    assert result is None


def test_cache_set_and_get_roundtrip(monkeypatch):
    """写入缓存后可以正确读取"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", True)
        monkeypatch.setenv("GENERATION_CACHE_DIR", tmpdir)

        payload = {"chapters": [{"id": "C001", "summary": "一段摘要"}]}
        set_cached_stage("chapter_analysis", "测试 prompt", payload)

        cached = get_cached_stage("chapter_analysis", "测试 prompt")
        assert cached == payload


def test_cache_disabled_returns_none(monkeypatch):
    """缓存关闭时即使有文件也返回 None"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", False)
        monkeypatch.setenv("GENERATION_CACHE_DIR", tmpdir)

        payload = {"key": "value"}
        set_cached_stage("test_stage", "test prompt", payload)

        # 缓存已关闭，get 应该返回 None
        result = get_cached_stage("test_stage", "test prompt")
        assert result is None


def test_cache_isolated_by_stage(monkeypatch):
    """不同 stage 的缓存互不干扰"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", True)
        monkeypatch.setenv("GENERATION_CACHE_DIR", tmpdir)

        set_cached_stage("stage_a", "相同 prompt", {"from": "a"})
        set_cached_stage("stage_b", "相同 prompt", {"from": "b"})

        assert get_cached_stage("stage_a", "相同 prompt") == {"from": "a"}
        assert get_cached_stage("stage_b", "相同 prompt") == {"from": "b"}


def test_cache_uses_content_hash(monkeypatch):
    """不同 prompt 使用不同的缓存文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", True)
        monkeypatch.setenv("GENERATION_CACHE_DIR", tmpdir)

        set_cached_stage("test", "prompt A", {"data": "A"})
        set_cached_stage("test", "prompt B", {"data": "B"})

        assert get_cached_stage("test", "prompt A") == {"data": "A"}
        assert get_cached_stage("test", "prompt B") == {"data": "B"}


def test_cache_corrupted_file_returns_none(monkeypatch):
    """损坏的缓存文件返回 None 不报错"""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", True)
        monkeypatch.setenv("GENERATION_CACHE_DIR", tmpdir)

        # 写入非法 JSON
        from app.services.generation_cache import _cache_path

        bad_path = _cache_path("test", "some prompt")
        bad_path.parent.mkdir(parents=True, exist_ok=True)
        bad_path.write_text("这不是 JSON", encoding="utf-8")

        result = get_cached_stage("test", "some prompt")
        assert result is None


def test_cache_directory_is_created(monkeypatch):
    """缓存目录不存在时自动创建"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_dir = Path(tmpdir) / "nonexistent" / "subdir"
        monkeypatch.setattr("app.services.generation_cache.settings.enable_generation_cache", True)
        monkeypatch.setenv("GENERATION_CACHE_DIR", str(cache_dir))

        assert not cache_dir.exists()
        set_cached_stage("test", "prompt", {"ok": True})
        assert cache_dir.exists()
        assert get_cached_stage("test", "prompt") == {"ok": True}
