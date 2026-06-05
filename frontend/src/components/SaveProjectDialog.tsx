import { X } from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useId, useRef, useState } from "react";

interface SaveProjectDialogProps {
  open: boolean;
  initialTitle: string;
  initialGenre: string;
  mode: "create" | "copy";
  onClose: () => void;
  onSubmit: (title: string, genre: string) => void;
}

export function SaveProjectDialog({ open, initialTitle, initialGenre, mode, onClose, onSubmit }: SaveProjectDialogProps) {
  const [title, setTitle] = useState(initialTitle);
  const [genre, setGenre] = useState(initialGenre);
  const headingId = useId();
  const titleInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (open) {
      setTitle(initialTitle);
      setGenre(initialGenre);
      window.setTimeout(() => titleInputRef.current?.focus(), 0);
    }
  }, [open, initialTitle, initialGenre]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onClose();
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!title.trim() || !genre.trim()) {
      return;
    }
    onSubmit(title.trim(), genre.trim());
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={(event) => {
      if (event.target === event.currentTarget) {
        onClose();
      }
    }}>
      <form className="modal-panel" role="dialog" aria-modal="true" aria-labelledby={headingId} onSubmit={handleSubmit}>
        <div className="panel-head">
          <div>
            <p className="panel-kicker">保存</p>
            <h2 id={headingId}>{mode === "copy" ? "另存为项目" : "保存当前项目"}</h2>
          </div>
          <button type="button" className="icon-button tiny" onClick={onClose} title="关闭" aria-label="关闭保存项目弹窗">
            <X className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>

        <label className="field">
          <span>项目标题</span>
          <input ref={titleInputRef} value={title} onChange={(event) => setTitle(event.target.value)} />
        </label>

        <label className="field">
          <span>剧本类型</span>
          <input value={genre} onChange={(event) => setGenre(event.target.value)} />
        </label>

        <div className="modal-actions">
          <button type="button" className="ghost-button" onClick={onClose}>取消</button>
          <button type="submit" className="primary-button" disabled={!title.trim() || !genre.trim()}>保存</button>
        </div>
      </form>
    </div>
  );
}
