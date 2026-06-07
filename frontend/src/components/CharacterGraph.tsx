import { Background, Controls, MarkerType, ReactFlow, type Edge, type Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useMemo } from "react";
import yaml from "js-yaml";

interface CharacterGraphProps {
  yamlText: string;
}

interface CharNode {
  id: string;
  name: string;
  role: string;
  description: string;
  relationships: Array<{ character_id: string; type: string }>;
}

const ROLE_COLORS: Record<string, string> = {
  主角: "#315d50",
  配角: "#5f7d6b",
  反派: "#8c2f22",
  路人: "#6c746f",
};

const ROLE_BG: Record<string, string> = {
  主角: "#e8f0ec",
  配角: "#eef3ef",
  反派: "#f7eae7",
  路人: "#f2f2ef",
};

/** 将字符排布在圆弧上 */
function circularLayout(nodes: CharNode[]): Node[] {
  const centerX = 300;
  const centerY = 250;
  const radius = Math.max(180, nodes.length * 50);
  return nodes.map((char, i) => {
    const angle = (2 * Math.PI * i) / nodes.length - Math.PI / 2;
    return {
      id: char.id,
      type: "default",
      position: {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      },
      data: {
        label: char.name,
        role: char.role,
        description: char.description,
      },
      style: {
        background: ROLE_BG[char.role] ?? "#f2f2ef",
        border: `2px solid ${ROLE_COLORS[char.role] ?? "#6c746f"}`,
        borderRadius: 10,
        padding: "8px 14px",
        fontSize: 13,
        fontWeight: 700,
        color: "#192026",
        minWidth: 100,
        textAlign: "center" as const,
      },
    };
  });
}

function buildEdges(chars: CharNode[], scenes: Array<{ characters?: string[] }>): Edge[] {
  const edges: Edge[] = [];
  const charMap = new Map(chars.map((c) => [c.id, c]));

  // 1. Explicit relationships
  for (const char of chars) {
    for (const rel of char.relationships ?? []) {
      if (charMap.has(rel.character_id)) {
        edges.push({
          id: `${char.id}-${rel.character_id}`,
          source: char.id,
          target: rel.character_id,
          label: rel.type,
          type: "smoothstep",
          animated: true,
          style: { stroke: "#88968d", strokeWidth: 2 },
          markerEnd: { type: MarkerType.ArrowClosed, color: "#88968d" },
        });
      }
    }
  }

  // 2. Scene co-occurrence (only if no explicit relationship yet)
  const paired = new Set(edges.map((e) => `${e.source}-${e.target}`));
  for (const scene of scenes) {
    const cids = (scene.characters ?? []).filter((id) => charMap.has(id));
    for (let i = 0; i < cids.length; i++) {
      for (let j = i + 1; j < cids.length; j++) {
        const key = `${cids[i]}-${cids[j]}`;
        if (!paired.has(key) && !paired.has(`${cids[j]}-${cids[i]}`)) {
          edges.push({
            id: `scene-${key}`,
            source: cids[i],
            target: cids[j],
            type: "default",
            style: { stroke: "#cbd4ce", strokeWidth: 1, strokeDasharray: "4 4" },
            label: "同场景",
          });
          paired.add(key);
        }
      }
    }
  }

  return edges;
}

export function CharacterGraph({ yamlText }: CharacterGraphProps) {
  const { nodes, edges } = useMemo(() => {
    if (!yamlText.trim()) return { nodes: [], edges: [] };

    try {
      const doc = yaml.load(yamlText) as any;
      const script = doc?.script;
      if (!script) return { nodes: [], edges: [] };

      const chars: CharNode[] = (script.characters ?? []).map((c: any) => ({
        id: c.id,
        name: c.name ?? "未命名",
        role: c.role ?? "路人",
        description: c.description ?? "",
        relationships: c.relationships ?? [],
      }));
      const scenes: Array<{ characters?: string[] }> = script.scenes ?? [];

      return {
        nodes: circularLayout(chars),
        edges: buildEdges(chars, scenes),
      };
    } catch {
      return { nodes: [], edges: [] };
    }
  }, [yamlText]);

  if (!nodes.length) return null;

  return (
    <section className="workspace-panel compact-panel character-graph-panel">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">可视化</p>
          <h2>角色关系网</h2>
        </div>
      </div>
      <div className="character-graph-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          proOptions={{ hideAttribution: true }}
          nodesDraggable
          panOnDrag
          zoomOnScroll
        >
          <Background color="#d7ddd8" gap={20} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </section>
  );
}
