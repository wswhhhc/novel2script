import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import { YamlEditor } from "../YamlEditor";

// Mock Monaco Editor to avoid loading issues in tests
vi.mock("@monaco-editor/react", () => ({
  default: ({ value, onChange }: { value: string; onChange: (val: string) => void }) => (
    <textarea data-testid="monaco-editor" value={value} onChange={(e) => onChange(e.target.value)} />
  ),
}));

describe("YamlEditor", () => {
  const mockOnYamlChange = vi.fn();
  const mockOnValidate = vi.fn();

  const defaultProps = {
    title: "测试剧本",
    yamlText: "script:\n  title: 测试",
    validation: null,
    generating: false,
    validating: false,
    onYamlChange: mockOnYamlChange,
    onValidate: mockOnValidate,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders editor panel", () => {
    render(<YamlEditor {...defaultProps} />);
    expect(screen.getByText(/YAML 剧本/i)).toBeInTheDocument();
  });

  it("shows copy button when yaml exists", () => {
    render(<YamlEditor {...defaultProps} />);
    expect(screen.getByText("复制")).toBeInTheDocument();
  });

  it("shows download button when yaml exists", () => {
    render(<YamlEditor {...defaultProps} />);
    expect(screen.getByText("下载")).toBeInTheDocument();
  });

  it("shows validate button", () => {
    render(<YamlEditor {...defaultProps} />);
    expect(screen.getByText("校验")).toBeInTheDocument();
  });

  it("calls onValidate when validate button is clicked", async () => {
    const user = userEvent.setup();
    render(<YamlEditor {...defaultProps} />);

    const validateBtn = screen.getByText("校验");
    await user.click(validateBtn);

    expect(mockOnValidate).toHaveBeenCalled();
  });

  it("disables buttons when no yaml content", () => {
    render(<YamlEditor {...defaultProps} yamlText="" />);

    const copyBtn = screen.getByRole('button', { name: /复制/i });
    const downloadBtn = screen.getByRole('button', { name: /下载/i });
    const validateBtn = screen.getByRole('button', { name: /校验/i });

    expect(copyBtn).toBeDisabled();
    expect(downloadBtn).toBeDisabled();
    expect(validateBtn).toBeDisabled();
  });

  it("shows validating state", () => {
    render(<YamlEditor {...defaultProps} validating={true} />);
    expect(screen.getByText("校验中")).toBeInTheDocument();
  });

  it("suppresses local syntax errors while generating", () => {
    render(<YamlEditor {...defaultProps} yamlText={'script:\n  title: "未完成'} generating={true} />);
    expect(screen.getAllByText("生成中").length).toBeGreaterThanOrEqual(1);
    expect(screen.queryByText("本地语法检查失败")).not.toBeInTheDocument();
  });

  it("displays validation success", () => {
    render(<YamlEditor {...defaultProps} validation={{ valid: true, errors: [] }} />);
    expect(screen.getByText(/校验通过/i)).toBeInTheDocument();
  });

  it("displays validation errors", () => {
    const validation = {
      valid: false,
      errors: ["缺少必填字段 title", "ID 格式错误"],
    };
    render(<YamlEditor {...defaultProps} validation={validation} />);

    expect(screen.getByText("Schema 校验失败")).toBeInTheDocument();
    expect(screen.getByText(/缺少必填字段 title/i)).toBeInTheDocument();
    expect(screen.getByText(/ID 格式错误/i)).toBeInTheDocument();
  });
});
