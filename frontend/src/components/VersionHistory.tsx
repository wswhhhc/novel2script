import { History, RotateCcw, Save } from "lucide-react";
import type { ScriptVersionSummary } from "../api/types";
import { formatDateTime } from "../utils/format";

interface VersionHistoryProps {
  versions: ScriptVersionSummary[];
  hasProject: boolean;
  loading: boolean;
  onCreateVersion: () => void;
  onRestoreVersion: (version: ScriptVersionSummary) => void;
}

export function VersionHistory({ versions, hasProject, loading, onCreateVersion, onRestoreVersion }: VersionHistoryProps) {
  return (
    <section className="version-panel">
      <div className="panel-head slim">
        <div>
          <p className="panel-kicker">版本</p>
          <h2>版本历史</h2>
        </div>
        <button type="button" className="icon-button" onClick={onCreateVersion} disabled={!hasProject || loading} title="保存版本快照">
          {loading ? <span className="spinner" /> : <Save className="h-4 w-4" aria-hidden="true" />}
          <span>快照</span>
        </button>
      </div>

      {versions.length === 0 ? (
        <div className="version-empty">
          <History className="h-4 w-4" aria-hidden="true" />
          <span>{hasProject ? "暂无版本快照" : "保存项目后可创建版本"}</span>
        </div>
      ) : (
        <div className="version-list">
          {versions.map((version) => (
            <div key={version.id} className="version-row">
              <div>
                <strong>{version.version_name}</strong>
                <span>{formatDateTime(version.created_at)}</span>
                {version.note ? <small>{version.note}</small> : null}
              </div>
              <button type="button" className="icon-button tiny" onClick={() => onRestoreVersion(version)} title="恢复此版本">
                <RotateCcw className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
