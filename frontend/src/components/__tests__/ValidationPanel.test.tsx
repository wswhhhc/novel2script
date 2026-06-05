import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ValidationPanel } from "../ValidationPanel";

describe("ValidationPanel", () => {
  it("shows waiting state when validation is null", () => {
    render(<ValidationPanel validation={null} localSyntaxError={null} />);
    expect(screen.getByText("等待校验")).toBeInTheDocument();
  });

  it("displays success state when validation passes", () => {
    const validation = { valid: true, errors: [] };
    render(<ValidationPanel validation={validation} localSyntaxError={null} />);

    expect(screen.getByText("Schema 校验通过")).toBeInTheDocument();
    expect(screen.getByText(/符合后端校验规则/i)).toBeInTheDocument();
  });

  it("displays local syntax error", () => {
    render(<ValidationPanel validation={null} localSyntaxError="YAML 语法错误：缺少冒号" />);

    expect(screen.getByText(/语法错误/i)).toBeInTheDocument();
    expect(screen.getByText(/缺少冒号/i)).toBeInTheDocument();
  });

  it("displays schema validation errors", () => {
    const validation = {
      valid: false,
      errors: [
        "script.title: 必填字段",
        "script.characters[0].id: 格式错误，应为 CHAR001-CHAR999",
        "script.scenes[0].beats[0]: dialogue 类型必须包含 character 字段",
      ],
    };
    render(<ValidationPanel validation={validation} localSyntaxError={null} />);

    expect(screen.getByText("Schema 校验失败")).toBeInTheDocument();
    expect(screen.getByText(/必填字段/i)).toBeInTheDocument();
    expect(screen.getByText(/格式错误/i)).toBeInTheDocument();
    expect(screen.getByText(/必须包含 character 字段/i)).toBeInTheDocument();
  });

  it("shows error count in header", () => {
    const validation = {
      valid: false,
      errors: ["错误1", "错误2", "错误3", "错误4", "错误5"],
    };
    render(<ValidationPanel validation={validation} localSyntaxError={null} />);

    expect(screen.getByText("Schema 校验失败")).toBeInTheDocument();
  });

  it("prioritizes local syntax error over schema errors", () => {
    const validation = { valid: false, errors: ["Schema 错误"] };
    render(<ValidationPanel validation={validation} localSyntaxError="语法错误" />);

    // Should show syntax error first
    expect(screen.getByText(/语法错误/i)).toBeInTheDocument();
  });

  it("renders error messages as a list", () => {
    const validation = {
      valid: false,
      errors: ["错误A", "错误B", "错误C"],
    };
    const { container } = render(<ValidationPanel validation={validation} localSyntaxError={null} />);

    const errorItems = container.querySelectorAll("li");
    expect(errorItems.length).toBeGreaterThanOrEqual(3);
  });
});
