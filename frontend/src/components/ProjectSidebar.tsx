import { FilePlus2, FolderOpen, RefreshCw, Trash2 } from "lucide-react";
import type { ProjectSummary } from "../api/types";
import { formatDateTime } from "../utils/format";

interface ProjectSidebarProps {
  projects: ProjectSummary[];
  currentProjectId: number | null;
  loading: boolean;
  onRefresh: () => void;
  onOpen: (projectId: number) => void;
  onDelete: (projectId: number) => void;
  onNew: () => void;
}

export function ProjectSidebar({
  projects,
  currentProjectId,
  loading,
  onRefresh,
  onOpen,
  onDelete,
  onNew,
}: ProjectSidebarProps) {
  return (
    <section className="workspace-panel project-sidebar">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">项目</p>
          <h2>本地项目</h2>
        </div>
        <div className="toolbar compact">
          <button type="button" className="icon-button" onClick={onNew} title="新建项目" aria-label="新建项目">
            <FilePlus2 className="h-4 w-4" aria-hidden="true" />
          </button>
          <button
            type="button"
            className="icon-button"
            onClick={onRefresh}
            disabled={loading}
            title="刷新项目列表"
            aria-label="刷新项目列表"
          >
            {loading ? <span className="spinner" /> : <RefreshCw className="h-4 w-4" aria-hidden="true" />}
          </button>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state compact-empty">
          <FolderOpen className="h-5 w-5" aria-hidden="true" />
          <p>暂无保存项目。</p>
        </div>
      ) : (
        <div className="project-list">
          {projects.map((project) => (
            <div key={project.id} className={`project-row ${project.id === currentProjectId ? "active" : ""}`}>
              <button type="button" className="project-main" onClick={() => onOpen(project.id)}>
                <strong>{project.title}</strong>
                <span>
                  {project.genre} · {project.chapter_count} 章
                </span>
                <small>{formatDateTime(project.updated_at)}</small>
              </button>
              <button
                type="button"
                className="icon-button danger tiny"
                onClick={() => onDelete(project.id)}
                title="删除项目"
                aria-label={`删除项目 ${project.title}`}
              >
                <Trash2 className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
