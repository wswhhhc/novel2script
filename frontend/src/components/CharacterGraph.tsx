import { useCallback, useMemo } from "react";
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

interface Character {
  id: string;
  name: string;
  role?: string;
  relationships?: Array<{
    character_id: string;
    relation: string;
  }>;
}

interface CharacterGraphProps {
  characters: Character[];
}

export function CharacterGraph({ characters }: CharacterGraphProps) {
  // 构建节点
  const initialNodes: Node[] = useMemo(() => {
    if (!characters || characters.length === 0) return [];

    return characters.map((char, index) => {
      const angle = (2 * Math.PI * index) / characters.length;
      const radius = 200;
      const x = 400 + radius * Math.cos(angle);
      const y = 300 + radius * Math.sin(angle);

      return {
        id: char.id,
        type: "default",
        position: { x, y },
        data: {
          label: (
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: "bold" }}>{char.name}</div>
              {char.role && <div style={{ fontSize: "0.8em", color: "#666" }}>{char.role}</div>}
            </div>
          ),
        },
        style: {
          background: getRoleColor(char.role),
          color: "#fff",
          border: "2px solid #222",
          borderRadius: "8px",
          padding: "10px",
          minWidth: "100px",
        },
      };
    });
  }, [characters]);

  // 构建边
  const initialEdges: Edge[] = useMemo(() => {
    if (!characters || characters.length === 0) return [];

    const edges: Edge[] = [];
    const processedPairs = new Set<string>();

    characters.forEach((char) => {
      if (!char.relationships) return;

      char.relationships.forEach((rel) => {
        // 避免双向关系重复显示
        const pairKey = [char.id, rel.character_id].sort().join("-");
        if (processedPairs.has(pairKey)) return;
        processedPairs.add(pairKey);

        edges.push({
          id: `${char.id}-${rel.character_id}`,
          source: char.id,
          target: rel.character_id,
          label: rel.relation,
          type: "smoothstep",
          animated: false,
          style: { stroke: "#666" },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 20,
            height: 20,
            color: "#666",
          },
          labelStyle: {
            fill: "#333",
            fontWeight: 500,
            fontSize: 12,
          },
          labelBgStyle: {
            fill: "#fff",
            fillOpacity: 0.8,
          },
        });
      });
    });

    return edges;
  }, [characters]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  if (!characters || characters.length === 0) {
    return <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>暂无角色数据</div>;
  }

  return (
    <div style={{ width: "100%", height: "600px", border: "1px solid #e2e8f0", borderRadius: "8px" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-left"
      >
        <Background color="#aaa" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const char = characters.find((c) => c.id === node.id);
            return getRoleColor(char?.role);
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
    </div>
  );
}

function getRoleColor(role?: string): string {
  if (!role) return "#94a3b8";

  const roleColors: Record<string, string> = {
    主角: "#3b82f6",
    配角: "#10b981",
    反派: "#ef4444",
    路人: "#94a3b8",
    龙套: "#6b7280",
  };

  return roleColors[role] || "#8b5cf6";
}
