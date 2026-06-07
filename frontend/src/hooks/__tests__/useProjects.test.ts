import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useProjects, type ProjectWorkspaceBridge } from "../useProjects";
import * as client from "../../api/client";

// Mock API client
vi.mock("../../api/client", () => ({
  listProjects: vi.fn(),
  getProject: vi.fn(),
  createProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
  listVersions: vi.fn(),
  createVersion: vi.fn(),
  restoreVersion: vi.fn(),
  exportProject: vi.fn(),
}));

function createMockBridge(): ProjectWorkspaceBridge {
  return {
    title: "",
    genre: "悬疑",
    content: "",
    yamlText: "",
    parseResult: null,
    validation: null,
    generationMode: undefined,
    dirty: false,
    applyProject: vi.fn(),
    resetWorkspace: vi.fn(),
    setStatus: vi.fn(),
  };
}

const mockProject = {
  id: 1,
  title: "测试项目",
  genre: "悬疑",
  chapter_count: 3,
  source_content: "正文内容",
  chapters: [{ id: "C001", title: "第一章", content: "内容", word_count: 100 }],
  current_yaml: "script:\n  title: 测试",
  validation: { valid: true, errors: [] },
  generation_mode: "mock" as const,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("useProjects", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(window, "confirm").mockReturnValue(true);
    // version name prompt returns "v1", note prompt returns ""
    vi.spyOn(window, "prompt").mockReturnValueOnce("v1").mockReturnValueOnce("");
  });

  it("initializes with empty state", () => {
    const bridge = createMockBridge();
    const { result } = renderHook(() => useProjects(bridge));

    expect(result.current.projects).toEqual([]);
    expect(result.current.currentProject).toBeNull();
    expect(result.current.currentProjectId).toBeNull();
    expect(result.current.versions).toEqual([]);
    expect(result.current.saveDialogMode).toBeNull();
  });

  it("loadProjects fetches project list", async () => {
    const projects = [mockProject];
    vi.mocked(client.listProjects).mockResolvedValueOnce(projects);

    const bridge = createMockBridge();
    const { result } = renderHook(() => useProjects(bridge));

    await act(async () => {
      await result.current.loadProjects();
    });

    expect(client.listProjects).toHaveBeenCalledTimes(1);
    expect(result.current.projects).toEqual(projects);
  });

  it("handleOpenProject fetches and applies project", async () => {
    vi.mocked(client.getProject).mockResolvedValueOnce(mockProject);
    vi.mocked(client.listVersions).mockResolvedValueOnce([]);

    const bridge = createMockBridge();
    const { result } = renderHook(() => useProjects(bridge));

    await act(async () => {
      await result.current.handleOpenProject(1);
    });

    expect(client.getProject).toHaveBeenCalledWith(1);
    expect(bridge.applyProject).toHaveBeenCalledWith(mockProject);
    expect(bridge.setStatus).toHaveBeenCalledWith(expect.objectContaining({ tone: "success" }));
  });

  it("handleOpenProject shows error on failure", async () => {
    vi.mocked(client.getProject).mockRejectedValueOnce(new Error("未找到"));

    const bridge = createMockBridge();
    const { result } = renderHook(() => useProjects(bridge));

    await act(async () => {
      await result.current.handleOpenProject(999);
    });

    expect(bridge.setStatus).toHaveBeenCalledWith(expect.objectContaining({ tone: "error" }));
  });

  it("handleDeleteProject removes project", async () => {
    vi.mocked(client.deleteProject).mockResolvedValueOnce({ message: "已删除", id: 1 });
    vi.mocked(client.listProjects).mockResolvedValueOnce([]);

    const bridge = createMockBridge();
    const { result } = renderHook(() => useProjects(bridge));

    // Set current project directly instead of going through handleOpenProject
    // to ensure clean state
    vi.mocked(client.getProject).mockResolvedValue(mockProject);
    vi.mocked(client.listVersions).mockResolvedValue([]);

    await act(async () => {
      await result.current.handleOpenProject(1);
    });

    expect(bridge.applyProject).toHaveBeenCalled(); // verify project was opened

    await act(async () => {
      await result.current.handleDeleteProject(1);
    });

    expect(client.deleteProject).toHaveBeenCalledWith(1);
    expect(bridge.resetWorkspace).toHaveBeenCalled();
  });

  it("handleSave opens save dialog when no current project", async () => {
    const bridge = createMockBridge();
    bridge.yamlText = "yaml: content";
    bridge.content = "正文";

    const { result } = renderHook(() => useProjects(bridge));

    await act(async () => {
      await result.current.handleSave();
    });

    expect(result.current.saveDialogMode).toBe("create");
  });

  it("handleSave saves existing project", async () => {
    vi.mocked(client.updateProject).mockResolvedValueOnce(mockProject);
    vi.mocked(client.listProjects).mockResolvedValueOnce([mockProject]);

    const bridge = createMockBridge();
    bridge.yamlText = "yaml: content";
    bridge.content = "正文";

    const { result } = renderHook(() => useProjects(bridge));

    // Set current project
    vi.mocked(client.getProject).mockResolvedValueOnce(mockProject);
    vi.mocked(client.listVersions).mockResolvedValueOnce([]);
    await act(async () => {
      await result.current.handleOpenProject(1);
    });

    await act(async () => {
      await result.current.handleSave();
    });

    expect(client.updateProject).toHaveBeenCalledWith(1, expect.any(Object));
  });

  it("handleCreateVersion creates version snapshot", async () => {
    vi.mocked(client.createVersion).mockResolvedValueOnce({
      id: 1,
      project_id: 1,
      version_name: "v1",
      note: "",
      created_at: "",
    });
    vi.mocked(client.listVersions).mockResolvedValueOnce([]);

    const bridge = createMockBridge();
    bridge.yamlText = "yaml: content";

    const { result } = renderHook(() => useProjects(bridge));

    // Set current project
    vi.mocked(client.getProject).mockResolvedValueOnce(mockProject);
    vi.mocked(client.listVersions).mockResolvedValueOnce([]);
    await act(async () => {
      await result.current.handleOpenProject(1);
    });

    await act(async () => {
      await result.current.handleCreateVersion();
    });

    expect(client.createVersion).toHaveBeenCalledWith(1, {
      version_name: "v1",
      yaml: "yaml: content",
      validation: null,
      note: "",
    });
  });
});
