import { LogOut, UserCircle2 } from "lucide-react";
import { useState } from "react";

interface WorkspaceBadgeProps {
  workspace: string;
  onChangeClick: () => void;
}

export function WorkspaceBadge({ workspace, onChangeClick }: WorkspaceBadgeProps) {
  const [showMenu, setShowMenu] = useState(false);

  if (!workspace) return null;

  return (
    <div className="workspace-badge-wrapper" style={{ position: "relative" }}>
      <button
        type="button"
        className="workspace-badge"
        onClick={() => setShowMenu((prev) => !prev)}
        title='点击切换工作区'
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          padding: "4px 10px",
          borderRadius: "var(--radius-sm, 6px)",
          border: "1px solid var(--color-border, #e0e0e0)",
          background: "var(--color-surface, #f5f5f5)",
          cursor: "pointer",
          fontSize: "0.8rem",
          color: "var(--color-text, #333)",
        }}
      >
        <UserCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
        <span>{workspace}</span>
      </button>

      {showMenu && (
        <>
          <div
            style={{ position: "fixed", inset: 0, zIndex: 99 }}
            onClick={() => setShowMenu(false)}
          />
          <div
            style={{
              position: "absolute",
              top: "calc(100% + 4px)",
              right: 0,
              zIndex: 100,
              background: "var(--color-bg, #fff)",
              border: "1px solid var(--color-border, #e0e0e0)",
              borderRadius: "var(--radius-sm, 6px)",
              boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
              minWidth: "140px",
              overflow: "hidden",
            }}
          >
            <button
              type="button"
              className="ghost-button"
              onClick={() => {
                setShowMenu(false);
                onChangeClick();
              }}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                width: "100%",
                padding: "8px 12px",
                border: "none",
                background: "transparent",
                cursor: "pointer",
                fontSize: "0.8rem",
              }}
            >
              <LogOut className="h-3.5 w-3.5" aria-hidden="true" />
              <span>切换工作区</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
