import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { CharacterGraph } from "../CharacterGraph";

// Mock @xyflow/react to avoid rendering the full canvas
vi.mock("@xyflow/react", () => ({
  ReactFlow: ({ nodes }: { nodes: Array<{ id: string; data: { label: string } }> }) => (
    <div data-testid="react-flow">
      {nodes.map((n) => (
        <div key={n.id} data-testid={`node-${n.id}`}>
          {n.data.label}
        </div>
      ))}
    </div>
  ),
  Background: () => null,
  Controls: () => null,
  MarkerType: { ArrowClosed: "arrowclosed" },
}));

// Mock js-yaml
vi.mock("js-yaml", () => ({
  default: {
    load: vi.fn(),
  },
}));

import yaml from "js-yaml";

describe("CharacterGraph", () => {
  it("renders nothing when yamlText is empty", () => {
    const { container } = render(<CharacterGraph yamlText="" />);
    expect(container.textContent).toBe("");
  });

  it("renders nothing when yamlText has no script key", () => {
    (yaml.load as ReturnType<typeof vi.fn>).mockReturnValue({});
    const { container } = render(<CharacterGraph yamlText="title: 无 script" />);
    expect(container.textContent).toBe("");
  });

  it("renders character nodes from valid YAML", () => {
    (yaml.load as ReturnType<typeof vi.fn>).mockReturnValue({
      script: {
        characters: [
          { id: "CHAR001", name: "张三", role: "主角", description: "男主", relationships: [] },
          { id: "CHAR002", name: "李四", role: "配角", description: "好友", relationships: [] },
        ],
        scenes: [],
      },
    });

    render(<CharacterGraph yamlText="script:\n  characters:\n    - id: CHAR001\n      name: 张三\n      role: 主角" />);

    expect(screen.getByText("张三")).toBeInTheDocument();
    expect(screen.getByText("李四")).toBeInTheDocument();
    expect(screen.getByTestId("react-flow")).toBeInTheDocument();
  });

  it("handles invalid YAML gracefully", () => {
    (yaml.load as ReturnType<typeof vi.fn>).mockImplementation(() => {
      throw new Error("parse error");
    });

    const { container } = render(<CharacterGraph yamlText="invalid: [" />);
    expect(container.textContent).toBe("");
  });

  it("renders relationship edges for linked characters", () => {
    (yaml.load as ReturnType<typeof vi.fn>).mockReturnValue({
      script: {
        characters: [
          { id: "CHAR001", name: "张三", role: "主角", description: "男主", relationships: [{ character_id: "CHAR002", type: "朋友" }] },
          { id: "CHAR002", name: "李四", role: "配角", description: "好友", relationships: [] },
        ],
        scenes: [],
      },
    });

    render(<CharacterGraph yamlText="..." />);

    expect(screen.getByText("张三")).toBeInTheDocument();
    expect(screen.getByText("李四")).toBeInTheDocument();
  });

  it("shows character role colors by role", () => {
    (yaml.load as ReturnType<typeof vi.fn>).mockReturnValue({
      script: {
        characters: [
          { id: "CHAR001", name: "主角", role: "主角", description: "", relationships: [] },
          { id: "CHAR002", name: "反派", role: "反派", description: "", relationships: [] },
        ],
        scenes: [],
      },
    });

    render(<CharacterGraph yamlText="..." />);

    expect(screen.getByText("主角")).toBeInTheDocument();
    expect(screen.getByText("反派")).toBeInTheDocument();
  });
});
