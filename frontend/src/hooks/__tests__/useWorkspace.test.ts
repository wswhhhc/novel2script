import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useWorkspace } from "../useWorkspace";
import * as client from "../../api/client";

// Mock API client
vi.mock("../../api/client", () => ({
  getGenerationMode: vi.fn(),
  parseChapters: vi.fn(),
  validateYaml: vi.fn(),
  generateScriptStream: vi.fn(),
}));

describe("useWorkspace", () => {
  const mockMode = {
    mode: "mock" as const,
    ai_enabled: false,
    provider: "openai",
    model: "deepseek-v4-flash",
    base_url_configured: false,
    api_key_configured: false,
    auto_fix_attempts: 3,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(client.getGenerationMode).mockResolvedValue(mockMode);
  });

  it("initializes with default state", () => {
    const { result } = renderHook(() => useWorkspace());

    expect(result.current.title).toBe("");
    expect(result.current.genre).toBe("悬疑");
    expect(result.current.content).toBe("");
    expect(result.current.yamlText).toBe("");
    expect(result.current.dirty).toBe(false);
    expect(result.current.canParse).toBe(false);
    expect(result.current.hasYaml).toBe(false);
  });

  it("loads generation mode on mount", async () => {
    const { result } = renderHook(() => useWorkspace());

    // Wait for effect
    await vi.waitFor(() => {
      expect(result.current.generationMode).toEqual(mockMode);
    });
  });

  it("handleTitleChange updates title and sets dirty", () => {
    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleTitleChange("测试小说"));

    expect(result.current.title).toBe("测试小说");
    expect(result.current.dirty).toBe(true);
  });

  it("handleGenreChange updates genre and sets dirty", () => {
    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleGenreChange("都市"));

    expect(result.current.genre).toBe("都市");
    expect(result.current.dirty).toBe(true);
  });

  it("handleContentChange resets parseResult and yaml", () => {
    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleContentChange("新内容"));

    expect(result.current.content).toBe("新内容");
    expect(result.current.parseResult).toBeNull();
    expect(result.current.yamlText).toBe("");
    expect(result.current.dirty).toBe(true);
  });

  it("handleYamlChange updates yaml and clears validation", () => {
    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleYamlChange("yaml: content"));

    expect(result.current.yamlText).toBe("yaml: content");
    expect(result.current.dirty).toBe(true);
  });

  it("handleParse calls API and updates state on success", async () => {
    const mockResult = {
      chapter_count: 3,
      valid: true,
      message: "识别成功",
      warnings: [],
      chapters: [
        { id: "C001", title: "第一章", content: "内容1", word_count: 100 },
        { id: "C002", title: "第二章", content: "内容2", word_count: 200 },
        { id: "C003", title: "第三章", content: "内容3", word_count: 300 },
      ],
    };
    vi.mocked(client.parseChapters).mockResolvedValueOnce(mockResult);

    const { result } = renderHook(() => useWorkspace());

    // First set content so canParse is true
    act(() => result.current.handleContentChange("第一章 内容\n第二章 内容\n第三章 内容"));

    await act(async () => {
      await result.current.handleParse();
    });

    expect(client.parseChapters).toHaveBeenCalledTimes(1);
    expect(result.current.parseResult).toEqual(mockResult);
    expect(result.current.dirty).toBe(true);
  });

  it("handleParse sets error status on API failure", async () => {
    vi.mocked(client.parseChapters).mockRejectedValueOnce(new Error("网络错误"));

    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleContentChange("第一章\n第二章\n第三章"));

    await act(async () => {
      await result.current.handleParse();
    });

    expect(result.current.status.tone).toBe("error");
  });

  it("canGenerate returns true only with valid parse result and 3+ chapters", () => {
    const { result } = renderHook(() => useWorkspace());

    expect(result.current.canParse).toBe(false);
    expect(result.current.canGenerate).toBe(false);

    act(() => result.current.handleContentChange("第一章\n第二章\n第三章"));

    expect(result.current.canParse).toBe(true);
    expect(result.current.canGenerate).toBe(false); // no parse yet

    act(() => {
      result.current.handleContentChange("第一章 内容\n第二章 内容\n第三章 内容");
    });

    expect(result.current.canParse).toBe(true);
  });

  it("handleValidate calls API and updates validation", async () => {
    const mockValidation = { valid: true, errors: [] };
    vi.mocked(client.validateYaml).mockResolvedValueOnce(mockValidation);

    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleYamlChange("script:\n  title: 测试"));

    await act(async () => {
      await result.current.handleValidate();
    });

    expect(client.validateYaml).toHaveBeenCalledTimes(1);
    expect(result.current.validation).toEqual(mockValidation);
    expect(result.current.status.tone).toBe("success");
  });

  it("handleValidate shows error on failure", async () => {
    const mockValidation = { valid: false, errors: ["标题不能为空"] };
    vi.mocked(client.validateYaml).mockResolvedValueOnce(mockValidation);

    const { result } = renderHook(() => useWorkspace());

    act(() => result.current.handleYamlChange("invalid: yaml"));

    await act(async () => {
      await result.current.handleValidate();
    });

    expect(result.current.validation).toEqual(mockValidation);
    expect(result.current.status.tone).toBe("error");
  });

  it("totalWords calculates correctly", () => {
    const { result } = renderHook(() => useWorkspace());

    expect(result.current.totalWords).toBe(0);

    act(() => {
      result.current.handleContentChange("第一章 内容\n第二章 内容\n第三章 内容");
    });

    // totalWords should still be 0 because parseResult is null
    expect(result.current.totalWords).toBe(0);
  });

  it("handleClear resets all state", () => {
    const { result } = renderHook(() => useWorkspace());

    act(() => {
      result.current.handleTitleChange("测试");
      result.current.handleContentChange("内容");
      result.current.handleYamlChange("yaml: 1");
    });

    act(() => result.current.handleClear());

    expect(result.current.title).toBe("");
    expect(result.current.content).toBe("");
    expect(result.current.yamlText).toBe("");
    expect(result.current.dirty).toBe(false);
  });
});
