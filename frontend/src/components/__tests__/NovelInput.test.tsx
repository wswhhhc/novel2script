import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import userEvent from "@testing-library/user-event";
import { NovelInput } from "../NovelInput";

describe("NovelInput", () => {
  const mockOnContentChange = vi.fn();
  const mockOnTitleChange = vi.fn();
  const mockOnGenreChange = vi.fn();
  const mockOnFileLoaded = vi.fn();
  const mockOnFileError = vi.fn();
  const mockOnClear = vi.fn();

  const defaultProps = {
    title: "",
    genre: "悬疑",
    content: "",
    onTitleChange: mockOnTitleChange,
    onGenreChange: mockOnGenreChange,
    onContentChange: mockOnContentChange,
    onFileLoaded: mockOnFileLoaded,
    onFileError: mockOnFileError,
    onClear: mockOnClear,
  };

  it("renders input fields", () => {
    render(<NovelInput {...defaultProps} />);
    expect(screen.getByText("小说标题")).toBeInTheDocument();
    expect(screen.getByText("剧本类型")).toBeInTheDocument();
    expect(screen.getByText("小说正文")).toBeInTheDocument();
  });

  it("calls onTitleChange when title is typed", async () => {
    const user = userEvent.setup();
    render(<NovelInput {...defaultProps} />);

    const titleInput = screen.getByPlaceholderText("用于生成和下载文件名");
    await user.type(titleInput, "测试小说");

    expect(mockOnTitleChange).toHaveBeenCalled();
  });

  it("calls onContentChange when content is typed", async () => {
    const user = userEvent.setup();
    render(<NovelInput {...defaultProps} />);

    const contentArea = screen.getByPlaceholderText(/粘贴包含至少 3 个章节/i);
    await user.type(contentArea, "第一章 开始");

    expect(mockOnContentChange).toHaveBeenCalled();
  });

  it("displays character count", () => {
    render(<NovelInput {...defaultProps} content="测试内容12345" />);
    expect(screen.getByText(/10/)).toBeInTheDocument();
  });

  it("shows clear button", () => {
    render(<NovelInput {...defaultProps} content="some content" />);
    expect(screen.getByText("清空")).toBeInTheDocument();
  });
});
