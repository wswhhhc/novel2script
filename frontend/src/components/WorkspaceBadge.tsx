import { LogOut, UserCircle2 } from "lucide-react";
import { useState } from "react";

interface WorkspaceBadgeProps {
  workspace: string;
  onSwitch: () => void;
}

export function WorkspaceBadge({ workspace, onSwitch }: WorkspaceBadgeProps) {
  const [showMenu, setShowMenu] = useState(false);

  if (!workspace) return null;

  return (
    <div className="relative">
      <button
        type="button"
        className="badge gap-1.5 cursor-pointer"
        onClick={() => setShowMenu((prev) => !prev)}
        title="点击切换工作区"
      >
        <UserCircle2 className="h-3.5 w-3.5" aria-hidden="true" />
        <span>{workspace}</span>
      </button>

      {showMenu && (
        <>
          <div className="fixed inset-0 z-[99]" onClick={() => setShowMenu(false)} />
          <div className="absolute right-0 top-full mt-1 z-[100] min-w-[140px] overflow-hidden rounded-md border bg-white shadow-lg">
            <button
              type="button"
              className="ghost-button w-full"
              onClick={() => {
                setShowMenu(false);
                onSwitch();
              }}
            >
              <LogOut className="h-3.5 w-3.5 mr-2 inline" aria-hidden="true" />
              <span>切换工作区</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
}
