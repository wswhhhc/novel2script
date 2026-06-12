import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import { ExportPanel } from "../ExportPanel";

describe("ExportPanel", () => {
  const mockOnExport = vi.fn();

  const defaultProps = {
    disabled: false,
    exporting: null as "yaml" | "json" | "markdown" | "pdf" | null,
    onExport: mockOnExport,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders all four format buttons", () => {
    render(<ExportPanel {...defaultProps} />);
    expect(screen.getByText("YAML")).toBeInTheDocument();
    expect(screen.getByText("JSON")).toBeInTheDocument();
    expect(screen.getByText("Markdown")).toBeInTheDocument();
    expect(screen.getByText("PDF")).toBeInTheDocument();
  });

  it("all buttons are enabled when disabled is false", () => {
    render(<ExportPanel {...defaultProps} />);

    const buttons = screen.getAllByRole("button");
    buttons.forEach((btn) => {
      expect(btn).not.toBeDisabled();
    });
  });

  it("all buttons are disabled when disabled is true", () => {
    render(<ExportPanel {...defaultProps} disabled={true} />);

    const buttons = screen.getAllByRole("button");
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled();
    });
  });

  it("calls onExport with correct format when button clicked", async () => {
    const user = userEvent.setup();
    render(<ExportPanel {...defaultProps} />);

    await user.click(screen.getByTitle("导出 YAML"));
    expect(mockOnExport).toHaveBeenCalledWith("yaml");

    await user.click(screen.getByTitle("导出 JSON"));
    expect(mockOnExport).toHaveBeenCalledWith("json");

    await user.click(screen.getByTitle("导出 Markdown"));
    expect(mockOnExport).toHaveBeenCalledWith("markdown");

    await user.click(screen.getByTitle("导出 PDF"));
    expect(mockOnExport).toHaveBeenCalledWith("pdf");
  });

  it("shows spinner on the currently exporting button", () => {
    render(<ExportPanel {...defaultProps} exporting="yaml" />);

    // YAML button should show spinner, others should show Download icon
    const yamlBtn = screen.getByTitle("导出 YAML");
    expect(yamlBtn.querySelector(".spinner")).toBeInTheDocument();

    const jsonBtn = screen.getByTitle("导出 JSON");
    expect(jsonBtn.querySelector(".lucide-download")).toBeInTheDocument();
  });

  it("disables all buttons while exporting", () => {
    render(<ExportPanel {...defaultProps} exporting="pdf" />);

    const buttons = screen.getAllByRole("button");
    buttons.forEach((btn) => {
      expect(btn).toBeDisabled();
    });
  });
});
