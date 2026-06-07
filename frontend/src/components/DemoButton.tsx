import { Sparkles } from "lucide-react";

interface DemoButtonProps {
  onClick: () => void;
  disabled: boolean;
  loading: boolean;
}

export function DemoButton({ onClick, disabled, loading }: DemoButtonProps) {
  return (
    <button
      type="button"
      className="demo-button"
      onClick={onClick}
      disabled={disabled || loading}
      title="一键加载演示数据并开始生成"
    >
      {loading ? (
        <span className="spinner" />
      ) : (
        <Sparkles className="h-4 w-4" aria-hidden="true" />
      )}
      <span>{loading ? "演示加载中…" : "快速演示"}</span>
    </button>
  );
}
