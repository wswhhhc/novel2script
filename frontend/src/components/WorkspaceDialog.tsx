import type { FormEvent } from "react";
import { useEffect, useId, useRef, useState } from "react";
import { isValidWorkspaceName } from "../utils/workspace";

interface WorkspaceDialogProps {
  open: boolean;
  onConfirm: (name: string) => void;
}

export function WorkspaceDialog({ open, onConfirm }: WorkspaceDialogProps) {
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const headingId = useId();
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (open) {
      setName("");
      setError("");
      window.setTimeout(() => inputRef.current?.focus(), 0);
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setError("");
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  if (!open) return null;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = name.trim();

    if (!trimmed) {
      setError("请输入工作区名称");
      return;
    }
    if (!isValidWorkspaceName(trimmed)) {
      setError("工作区名称只能包含字母、数字、中划线、下划线和中文");
      return;
    }
    onConfirm(trimmed);
  }

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          // 点击背景不关闭——必须输入工作区名称
        }
      }}
    >
      <form className="modal-panel" role="dialog" aria-modal="true" aria-labelledby={headingId} onSubmit={handleSubmit}>
        <div className="panel-head">
          <div>
            <p className="panel-kicker">欢迎使用 Novel2Script</p>
            <h2 id={headingId}>进入工作区</h2>
          </div>
        </div>

        <p style={{ margin: "0 0 12px", color: "#56615c", fontSize: "0.875rem", lineHeight: 1.5 }}>
          工作区用于隔离不同用户的数据。输入你的工作区名称，不同工作区之间的项目互不可见。
        </p>

        <label className="field">
          <span>工作区名称</span>
          <input
            ref={inputRef}
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setError("");
            }}
            placeholder="例如：my-project 或 张三"
          />
        </label>

        {error && <p style={{ color: "#b9472f", fontSize: "0.8rem", margin: "4px 0 0" }}>{error}</p>}

        <div className="modal-actions" style={{ marginTop: "16px" }}>
          <button type="submit" className="primary-button" disabled={!name.trim()}>
            进入工作区
          </button>
        </div>
      </form>
    </div>
  );
}
