import { AlertTriangle, Moon, RefreshCw, Sun } from "lucide-react";
import { CopyPlus, Save, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { getDemoInfo } from "./api/client";
import { ChapterList } from "./components/ChapterList";
import { CharacterGraph } from "./components/CharacterGraph";
import { ErrorBoundary } from "./components/ErrorBoundary";
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
import { useTheme } from "./hooks/useTheme";
import { useWorkspace } from "./hooks/useWorkspace";
import { getWorkspace, setWorkspace } from "./utils/workspace";

/** 区域级错误 fallback：某列崩溃时只替换该列区域，不影响其他区域。 */
function columnError(error: Error | null, reset: () => void) {
  return (
    <div className="column-error" role="alert">
      <AlertTriangle className="column-error-icon" aria-hidden="true" />
      <p>该区域发生异常，请尝试恢复或刷新页面。</p>
      {error && (
        <details className="column-error-details">
          <summary>错误详情</summary>
          <pre>{error.message}</pre>
        </details>
      )}
      <button type="button" className="ghost-button column-error-retry" onClick={reset}>
        <RefreshCw className="h-4 w-4" aria-hidden="true" />
        恢复
      </button>
    </div>
  );
}

function App() {
  const { theme, toggle: toggleTheme } = useTheme();
  const [workspace, setWorkspaceState] = useState<string>(() => getWorkspace());
  const [showWorkspaceDialog, setShowWorkspaceDialog] = useState(!getWorkspace());
  const [demoLoading, setDemoLoading] = useState(false);

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

  const ws = useWorkspace();

  async function handleRunDemo() {
    if (demoLoading || ws.generating || ws.parsing) return;
    setDemoLoading(true);
    ws._internal.setStatus({ tone: "info", message: "正在加载演示数据…" });
    try {
      const demo = await getDemoInfo();
      ws._internal.setTitle(demo.title);
      ws._internal.setGenre(demo.genre);
      ws._internal.setContent(demo.content);
      ws._internal.setParseResult(null);
      ws._internal.setYamlText("");
      ws._internal.setValidation(null);
      ws._internal.setDirty(true);
      ws._internal.setStatus({ tone: "success", message: `已加载演示小说《${demo.title}》，开始识别章节…` });

      // 自动触发章节识别
      ws.handleParse();
    } catch (err) {
      ws._internal.setStatus({
        tone: "error",
        message: err instanceof Error ? err.message : "加载演示数据失败",
      });
    } finally {
      setDemoLoading(false);
    }
  }

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
              className="demo-trigger"
              onClick={handleRunDemo}
              disabled={demoLoading || ws.generating || ws.parsing}
              title="一键加载演示小说并自动生成"
            >
              {demoLoading ? (
                <span className="spinner" />
              ) : (
                <Sparkles className="h-4 w-4" aria-hidden="true" />
              )}
              <span>{demoLoading ? "加载中…" : "快速演示"}</span>
            </button>
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
            <button
              type="button"
              className="icon-button theme-toggle"
              onClick={toggleTheme}
              title={theme === "light" ? "切换为暗色模式" : "切换为亮色模式"}
              aria-label="切换主题"
            >
              {theme === "light" ? (
                <Moon className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Sun className="h-4 w-4" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </header>

      <main className="workspace">
        <ErrorBoundary fallback={columnError}>
          <ProjectSidebar
            projects={projects.projects}
            currentProjectId={projects.currentProjectId}
            loading={projects.projectLoading}
            onRefresh={projects.loadProjects}
            onOpen={projects.handleOpenProject}
            onDelete={projects.handleDeleteProject}
            onNew={projects.handleNewProject}
          />
        </ErrorBoundary>

        <ErrorBoundary fallback={columnError}>
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
        </ErrorBoundary>

        <ErrorBoundary fallback={columnError}>
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
        </ErrorBoundary>

        <ErrorBoundary fallback={columnError}>
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
            <CharacterGraph yamlText={ws.yamlText} />
            <VersionHistory
              versions={projects.versions}
              hasProject={Boolean(projects.currentProject)}
              loading={projects.versionLoading}
              onCreateVersion={projects.handleCreateVersion}
              onRestoreVersion={projects.handleRestoreVersion}
            />
          </div>
        </ErrorBoundary>
      </main>

      <SaveProjectDialog
        open={projects.saveDialogMode !== null}
        initialTitle={ws.title || "未命名项目"}
        initialGenre={ws.genre || "未分类"}
        mode={projects.saveDialogMode ?? "create"}
        onClose={() => projects.setSaveDialogMode(null)}
        onSubmit={projects.handleSaveDialogSubmit}
      />

      <WorkspaceDialog open={showWorkspaceDialog} onConfirm={handleWorkspaceConfirm} />
    </div>
  );
}

export default App;
