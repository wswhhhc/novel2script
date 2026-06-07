import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../App";

// Mock all API client functions that App indirectly calls
vi.mock("../api/client", () => ({
  getGenerationMode: vi.fn().mockResolvedValue({
    mode: "mock",
    ai_enabled: false,
    provider: "openai",
    model: "deepseek-v4-flash",
    base_url_configured: false,
    api_key_configured: false,
    auto_fix_attempts: 3,
  }),
  listProjects: vi.fn().mockResolvedValue([]),
  parseChapters: vi.fn(),
  validateYaml: vi.fn(),
  generateScriptStream: vi.fn(),
  createProject: vi.fn(),
  getProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
  listVersions: vi.fn().mockResolvedValue([]),
  createVersion: vi.fn(),
  restoreVersion: vi.fn(),
  exportProject: vi.fn(),
}));

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the app shell with title and header", () => {
    render(<App />);

    expect(screen.getByText("Novel2Script 工作台")).toBeInTheDocument();
    expect(screen.getByText(/未保存项目/)).toBeInTheDocument();
  });

  it("shows initial status message", () => {
    render(<App />);

    expect(screen.getByText("粘贴小说正文或上传文件后开始识别章节。")).toBeInTheDocument();
  });

  it("renders all 3 column layout", () => {
    render(<App />);

    expect(screen.getByText("识别章节")).toBeInTheDocument();
    expect(screen.getByText("保存")).toBeInTheDocument();
  });

  it("updates word count when typing content", async () => {
    const user = userEvent.setup();
    render(<App />);

    const textarea = screen.getByPlaceholderText(/粘贴包含至少 3 个章节的小说文本/i);
    await user.type(textarea, "测试小说正文内容");

    // After typing, content metrics should be visible
    expect(screen.getByText("识别章节")).toBeInTheDocument();
    // Content length metrics rendered in the topbar
    expect(screen.getByText(/字输入/)).toBeTruthy();
  });

  it("disables generate button when no chapters parsed", () => {
    render(<App />);

    const generateBtn = screen.getByText("生成剧本").closest("button");
    expect(generateBtn).toBeDisabled();
  });

  it("save button is disabled when no yaml content", () => {
    render(<App />);

    const saveBtn = screen.getByText("保存").closest("button");
    expect(saveBtn).toBeDisabled();
  });

  it("shows project sidebar with new project button", () => {
    render(<App />);

    expect(screen.getByLabelText("新建项目")).toBeInTheDocument();
  });

  it("renders genre dropdown with default value", () => {
    render(<App />);

    const genreSelect = screen.getByDisplayValue("悬疑");
    expect(genreSelect).toBeInTheDocument();
  });

  it("renders export panel", () => {
    render(<App />);

    expect(screen.getByText("YAML")).toBeInTheDocument();
    expect(screen.getByText("JSON")).toBeInTheDocument();
    expect(screen.getByText("Markdown")).toBeInTheDocument();
  });

  it("shows statistics in topbar", () => {
    render(<App />);

    expect(screen.getByText(/0 字输入/)).toBeInTheDocument();
    expect(screen.getByText(/0 章/)).toBeInTheDocument();
    expect(screen.getByText(/0 字已识别/)).toBeInTheDocument();
  });
});
