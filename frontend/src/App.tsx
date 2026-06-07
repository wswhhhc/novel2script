import { CopyPlus, Save } from "lucide-react";
import { useEffect, useState } from "react";
import { ChapterList } from "./components/ChapterList";
import { ExportPanel } from "./components/ExportPanel";
import { GenerationPanel } from "./components/GenerationPanel";
import { NovelInput } from "./components/NovelInput";
import { ProjectSidebar } from "./components/ProjectSidebar";
import { SaveProjectDialog } from "./components/SaveProjectDialog";
import { StatusBanner, type BannerTone } from "./components/StatusBanner";
import { VersionHistory } from "./components/VersionHistory";
import { WorkspaceBadge } from "./components/WorkspaceBadge";
import { WorkspaceDialog } from "./components/WorkspaceDialog";
import { YamlEditor } from "./components/YamlEditor";
import { useProjects } from "./hooks/useProjects";
import { useWorkspace } from "./hooks/useWorkspace";
import { getWorkspace, setWorkspace } from "./utils/workspace";

function App() {
  const [workspace, setWorkspaceState] = useState<string>(() => getWorkspace());
  const [showWorkspaceDialog, setShowWorkspaceDialog] = useState(!getWorkspace());

  function handleWorkspaceConfirm(name: string) {
    setWorkspace(name);
    setWorkspaceState(name);
    setShowWorkspaceDialog(false);
  }

  function handleSwitchWorkspace() {
    setWorkspace("");
    setWorkspaceState("");
    setShowWorkspaceDialog(true);
  }

  // 工作区确认后自动加载项目列表
  useEffect(() => {
    if (workspace) {
      projects.loadProjects();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [workspace]);
  const ws = useWorkspace();
  const projects = useProjects({
    get title() {
      return ws.title;
    },
    get genre() {
      return ws.genre;
    },
    get content() {
      return ws.content;
    },
    get yamlText() {
      return ws.yamlText;
    },
    get parseResult() {
      return ws.parseResult;
    },
    get validation() {
      return ws.validation;
    },
    get generationMode() {
      return ws.generationMode?.mode;
    },
    get dirty() {
      return ws.dirty;
    },
    applyProject(project) {
      ws._internal.setTitle(project.title);
      ws._internal.setGenre(project.genre);
      ws._internal.setContent(project.source_content);
      ws._internal.setParseResult({
        chapter_count: project.chapter_count,
        valid: project.chapter_count >= 3,
        message: "已从保存项目恢复章节结果。",
        warnings: [],
        chapters: project.chapters,
      });
      ws._internal.setYamlText(project.current_yaml);
      ws._internal.setValidation(project.validation);
      ws._internal.setDirty(false);
    },
    resetWorkspace(msg) {
      ws._internal.setTitle("");
      ws._internal.setGenre("悬疑");
      ws._internal.setContent("");
      ws._internal.setParseResult(null);
      ws._internal.setYamlText("");
      ws._internal.setValidation(null);
      ws._internal.setDirty(false);
      ws._internal.setStatus({ tone: "info", message: msg ?? "已清空输入内容。" });
    },
    setStatus(s) {
      ws._internal.setStatus(s);
    },
  });

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Novel2Script 工作台</h1>
          <p>
            当前项目：{projects.currentProject ? projects.currentProject.title : "未保存项目"} ·{" "}
            {ws.dirty ? "有未保存修改" : "已保存"}
          </p>
        </div>
        <div className="topbar-actions">
          <WorkspaceBadge workspace={workspace} onSwitch={handleSwitchWorkspace} />
          <div className="topbar-metrics" aria-label="工作台统计">
            <span>{ws.content.length.toLocaleString()} 字输入</span>
            <span>{ws.parseResult?.chapter_count ?? 0} 章</span>
            <span>{ws.totalWords.toLocaleString()} 字已识别</span>
          </div>
          <div className="toolbar">
            <button
              type="button"
              className="icon-button strong"
              onClick={projects.handleSave}
              disabled={projects.saving || !ws.yamlText.trim()}
              title="保存项目"
            >
              {projects.saving ? <span className="spinner" /> : <Save className="h-4 w-4" aria-hidden="true" />}
              <span>保存</span>
            </button>
            <button
              type="button"
              className="icon-button"
              onClick={projects.handleSaveAs}
              disabled={projects.saving || !ws.yamlText.trim()}
              title="另存为项目"
            >
              <CopyPlus className="h-4 w-4" aria-hidden="true" />
              <span>另存为</span>
            </button>
            <ExportPanel
              disabled={!projects.currentProject || projects.exporting !== null}
              exporting={projects.exporting}
              onExport={projects.handleExport}
            />
          </div>
        </div>
      </header>

      <main className="workspace">
        <ProjectSidebar
          projects={projects.projects}
          currentProjectId={projects.currentProjectId}
          loading={projects.projectLoading}
          onRefresh={projects.loadProjects}
          onOpen={projects.handleOpenProject}
          onDelete={projects.handleDeleteProject}
          onNew={projects.handleNewProject}
        />

        <div className="left-column">
          <NovelInput
            title={ws.title}
            genre={ws.genre}
            content={ws.content}
            onTitleChange={ws.handleTitleChange}
            onGenreChange={ws.handleGenreChange}
            onContentChange={ws.handleContentChange}
            onFileLoaded={ws.handleFileLoaded}
            onFileError={(msg) => ws.setStatus({ tone: "error", message: msg })}
            onClear={ws.handleClear}
          />
        </div>

        <div className="middle-column">
          <StatusBanner tone={ws.status.tone as BannerTone} message={ws.status.message} />
          <GenerationPanel
            canParse={ws.canParse}
            canGenerate={ws.canGenerate}
            parsing={ws.parsing}
            generating={ws.generating}
            validating={ws.validating}
            generationProgress={ws.generationProgress}
            generationMessage={ws.generationMessage}
            chapterCount={ws.parseResult?.chapter_count ?? 0}
            generationMode={ws.generationMode}
            onParse={ws.handleParse}
            onGenerate={ws.handleGenerate}
          />
          <ChapterList result={ws.parseResult} />
        </div>

        <div className="right-column">
          <YamlEditor
            title={ws.title}
            yamlText={ws.yamlText}
            validation={ws.validation}
            generating={ws.generating}
            validating={ws.validating}
            onYamlChange={ws.handleYamlChange}
            onValidate={ws.handleValidate}
          />
          <VersionHistory
            versions={projects.versions}
            hasProject={Boolean(projects.currentProject)}
            loading={projects.versionLoading}
            onCreateVersion={projects.handleCreateVersion}
            onRestoreVersion={projects.handleRestoreVersion}
          />
        </div>
      </main>

      <SaveProjectDialog
        open={projects.saveDialogMode !== null}
        initialTitle={ws.title || "未命名项目"}
        initialGenre={ws.genre || "未分类"}
        mode={projects.saveDialogMode ?? "create"}
        onClose={() => projects.setSaveDialogMode(null)}
        onSubmit={projects.handleSaveDialogSubmit}
      />

      <WorkspaceDialog
        open={showWorkspaceDialog}
        onConfirm={handleWorkspaceConfirm}
      />
    </div>
  );
}

export default App;
