import { CopyPlus, Save } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  createProject,
  createVersion,
  deleteProject,
  exportProject,
  generateScript,
  getGenerationMode,
  getProject,
  listProjects,
  listVersions,
  parseChapters,
  restoreVersion,
  updateProject,
  validateYaml,
} from "./api/client";
import type {
  ExportFormat,
  GenerationModeResponse,
  ParseChaptersResponse,
  ProjectDetail,
  ProjectPayload,
  ProjectSummary,
  ScriptVersionSummary,
  ValidationResponse,
} from "./api/types";
import { ChapterList } from "./components/ChapterList";
import { ExportPanel } from "./components/ExportPanel";
import { GenerationPanel } from "./components/GenerationPanel";
import { NovelInput } from "./components/NovelInput";
import { ProjectSidebar } from "./components/ProjectSidebar";
import { SaveProjectDialog } from "./components/SaveProjectDialog";
import { StatusBanner, type BannerTone } from "./components/StatusBanner";
import { VersionHistory } from "./components/VersionHistory";
import { YamlEditor } from "./components/YamlEditor";
import { downloadBlob } from "./utils/download";

interface AppStatus {
  tone: BannerTone;
  message: string;
}

type SaveDialogMode = "create" | "copy" | null;

function App() {
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("悬疑");
  const [content, setContent] = useState("");
  const [parseResult, setParseResult] = useState<ParseChaptersResponse | null>(null);
  const [yamlText, setYamlText] = useState("");
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [status, setStatus] = useState<AppStatus>({ tone: "info", message: "粘贴小说正文或上传文件后开始识别章节。" });
  const [generationMode, setGenerationMode] = useState<GenerationModeResponse | null>(null);
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [currentProject, setCurrentProject] = useState<ProjectDetail | null>(null);
  const [versions, setVersions] = useState<ScriptVersionSummary[]>([]);
  const [saveDialogMode, setSaveDialogMode] = useState<SaveDialogMode>(null);
  const [dirty, setDirty] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [validating, setValidating] = useState(false);
  const [projectLoading, setProjectLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [versionLoading, setVersionLoading] = useState(false);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);

  const canParse = content.trim().length > 0;
  const canGenerate = Boolean(parseResult?.valid && parseResult.chapter_count >= 3 && parseResult.chapters.length >= 3);
  const hasYaml = yamlText.trim().length > 0;
  const currentProjectId = currentProject?.id ?? null;

  const totalWords = useMemo(
    () => parseResult?.chapters.reduce((sum, chapter) => sum + chapter.word_count, 0) ?? 0,
    [parseResult]
  );

  useEffect(() => {
    let mounted = true;

    getGenerationMode()
      .then((mode) => {
        if (mounted) {
          setGenerationMode(mode);
        }
      })
      .catch(() => {
        if (mounted) {
          setGenerationMode(null);
        }
      });

    loadProjects();

    return () => {
      mounted = false;
    };
  }, []);

  async function loadProjects() {
    setProjectLoading(true);
    try {
      setProjects(await listProjects());
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目列表加载失败" });
    } finally {
      setProjectLoading(false);
    }
  }

  async function loadVersions(projectId: number) {
    setVersionLoading(true);
    try {
      setVersions(await listVersions(projectId));
    } catch (error) {
      setVersions([]);
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本历史加载失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleParse() {
    if (!canParse || parsing) {
      return;
    }

    setParsing(true);
    setStatus({ tone: "info", message: "正在识别章节..." });

    try {
      const result = await parseChapters(content);
      setParseResult(result);
      setDirty(true);
      setStatus({
        tone: result.valid ? (result.warnings.length > 0 ? "warning" : "success") : "error",
        message: result.message,
      });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "章节识别请求失败" });
    } finally {
      setParsing(false);
    }
  }

  async function handleGenerate() {
    if (!canGenerate || !parseResult || generating) {
      return;
    }

    if (!title.trim()) {
      setStatus({ tone: "warning", message: "生成剧本前请填写小说标题。" });
      return;
    }

    setGenerating(true);
    setStatus({ tone: "info", message: "正在生成 YAML 剧本..." });

    try {
      const result = await generateScript(title.trim(), genre.trim() || "未分类", parseResult.chapters);
      setYamlText(result.yaml);
      setValidation(result.validation);
      setDirty(true);
      setStatus({
        tone: result.validation.valid ? "success" : "warning",
        message: result.validation.valid ? "剧本生成成功，Schema 校验通过。" : "剧本生成成功，但 Schema 校验有错误。",
      });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "剧本生成请求失败" });
    } finally {
      setGenerating(false);
    }
  }

  async function handleValidate() {
    if (!hasYaml || validating) {
      return;
    }

    setValidating(true);
    setStatus({ tone: "info", message: "正在调用后端校验 YAML..." });

    try {
      const result = await validateYaml(yamlText);
      setValidation(result);
      setDirty(true);
      setStatus({
        tone: result.valid ? "success" : "error",
        message: result.valid ? "YAML 校验通过。" : "YAML 校验失败，请查看错误列表。",
      });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "YAML 校验请求失败" });
    } finally {
      setValidating(false);
    }
  }

  function handleFileLoaded(fileContent: string, fileName: string) {
    setContent(fileContent);
    setParseResult(null);
    setYamlText("");
    setValidation(null);
    setDirty(true);
    setStatus({ tone: "success", message: `已读取文件：${fileName}` });
  }

  function handleTitleChange(value: string) {
    setTitle(value);
    setDirty(true);
  }

  function handleGenreChange(value: string) {
    setGenre(value);
    setDirty(true);
  }

  function handleContentChange(value: string) {
    setContent(value);
    setParseResult(null);
    setYamlText("");
    setValidation(null);
    setDirty(true);
  }

  function handleYamlChange(value: string) {
    setYamlText(value);
    setValidation(null);
    setDirty(true);
  }

  function resetWorkspace(message = "已清空输入内容。") {
    setTitle("");
    setGenre("悬疑");
    setContent("");
    setParseResult(null);
    setYamlText("");
    setValidation(null);
    setCurrentProject(null);
    setVersions([]);
    setDirty(false);
    setStatus({ tone: "info", message });
  }

  function handleClear() {
    resetWorkspace();
  }

  function handleNewProject() {
    if (dirty && !window.confirm("当前内容有未保存修改，确定新建项目吗？")) {
      return;
    }
    resetWorkspace("已新建空白项目。");
  }

  async function handleOpenProject(projectId: number) {
    if (dirty && currentProjectId !== projectId && !window.confirm("当前内容有未保存修改，确定打开其他项目吗？")) {
      return;
    }

    setProjectLoading(true);
    try {
      const project = await getProject(projectId);
      applyProject(project);
      await loadVersions(project.id);
      setStatus({ tone: "success", message: `已打开项目：${project.title}` });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目打开失败" });
    } finally {
      setProjectLoading(false);
    }
  }

  async function handleDeleteProject(projectId: number) {
    if (!window.confirm("删除后无法恢复，确定删除这个项目吗？")) {
      return;
    }

    try {
      await deleteProject(projectId);
      await loadProjects();
      if (currentProjectId === projectId) {
        resetWorkspace("当前项目已删除。");
      } else {
        setStatus({ tone: "success", message: "项目已删除。" });
      }
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目删除失败" });
    }
  }

  async function handleSave() {
    if (!hasYaml) {
      setStatus({ tone: "warning", message: "请先生成或填写 YAML 剧本，再保存项目。" });
      return;
    }
    if (!content.trim()) {
      setStatus({ tone: "warning", message: "保存项目前需要保留小说正文。" });
      return;
    }
    if (!currentProject) {
      setSaveDialogMode("create");
      return;
    }
    await saveExistingProject();
  }

  async function handleSaveAs() {
    if (!hasYaml || !content.trim()) {
      setStatus({ tone: "warning", message: "另存为前需要小说正文和 YAML 剧本。" });
      return;
    }
    setSaveDialogMode("copy");
  }

  async function handleSaveDialogSubmit(nextTitle: string, nextGenre: string) {
    setSaveDialogMode(null);
    await createNewProject(nextTitle, nextGenre);
  }

  async function saveExistingProject() {
    if (!currentProject) {
      return;
    }

    setSaving(true);
    setStatus({ tone: "info", message: "正在保存项目..." });
    try {
      const project = await updateProject(currentProject.id, buildProjectPayload(title, genre));
      applyProject(project);
      await loadProjects();
      setStatus({ tone: project.validation.valid ? "success" : "warning", message: "项目已保存。" });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目保存失败" });
    } finally {
      setSaving(false);
    }
  }

  async function createNewProject(nextTitle: string, nextGenre: string) {
    setSaving(true);
    setStatus({ tone: "info", message: "正在创建项目..." });
    try {
      const summary = await createProject(buildProjectPayload(nextTitle, nextGenre));
      const project = await getProject(summary.id);
      applyProject(project);
      await loadProjects();
      await loadVersions(project.id);
      setStatus({ tone: project.validation.valid ? "success" : "warning", message: `项目已保存：${project.title}` });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目创建失败" });
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateVersion() {
    if (!currentProject) {
      setStatus({ tone: "warning", message: "请先保存项目，再创建版本快照。" });
      return;
    }
    if (!hasYaml) {
      setStatus({ tone: "warning", message: "YAML 为空，不能创建版本快照。" });
      return;
    }

    const versionName = window.prompt("请输入版本名称", `版本 ${versions.length + 1}`);
    if (!versionName?.trim()) {
      return;
    }
    const note = window.prompt("版本说明（可选）", "") ?? "";

    setVersionLoading(true);
    try {
      await createVersion(currentProject.id, {
        version_name: versionName.trim(),
        yaml: yamlText,
        validation,
        note,
      });
      await loadVersions(currentProject.id);
      setStatus({ tone: "success", message: `已保存版本：${versionName.trim()}` });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本保存失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleRestoreVersion(version: ScriptVersionSummary) {
    if (!currentProject || !window.confirm(`确定恢复到版本“${version.version_name}”吗？当前 YAML 会被覆盖。`)) {
      return;
    }

    setVersionLoading(true);
    try {
      const project = await restoreVersion(currentProject.id, version.id);
      applyProject(project);
      await loadProjects();
      await loadVersions(project.id);
      setStatus({
        tone: project.validation.valid ? "success" : "warning",
        message: `已恢复到版本：${version.version_name}`,
      });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本恢复失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleExport(format: ExportFormat) {
    if (!currentProject) {
      setStatus({ tone: "warning", message: "请先保存项目，再使用后端导出。" });
      return;
    }

    setExporting(format);
    try {
      const result = await exportProject(currentProject.id, format);
      downloadBlob(result.blob, result.filename);
      setStatus({ tone: "success", message: `已导出 ${format === "markdown" ? "Markdown" : format.toUpperCase()}。` });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "导出失败" });
    } finally {
      setExporting(null);
    }
  }

  function buildProjectPayload(nextTitle: string, nextGenre: string): ProjectPayload {
    return {
      title: nextTitle.trim(),
      genre: nextGenre.trim() || "未分类",
      source_content: content,
      chapters: parseResult?.chapters ?? [],
      yaml: yamlText,
      validation,
      generation_mode: generationMode?.mode ?? currentProject?.generation_mode ?? "mock",
    };
  }

  function applyProject(project: ProjectDetail) {
    setCurrentProject(project);
    setTitle(project.title);
    setGenre(project.genre);
    setContent(project.source_content);
    setParseResult({
      chapter_count: project.chapter_count,
      valid: project.chapter_count >= 3,
      message: "已从保存项目恢复章节结果。",
      warnings: [],
      chapters: project.chapters,
    });
    setYamlText(project.current_yaml);
    setValidation(project.validation);
    setDirty(false);
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Novel2Script 工作台</h1>
          <p>
            当前项目：{currentProject ? currentProject.title : "未保存项目"} · {dirty ? "有未保存修改" : "已保存"}
          </p>
        </div>
        <div className="topbar-actions">
          <div className="topbar-metrics" aria-label="工作台统计">
            <span>{content.length.toLocaleString()} 字输入</span>
            <span>{parseResult?.chapter_count ?? 0} 章</span>
            <span>{totalWords.toLocaleString()} 字已识别</span>
          </div>
          <div className="toolbar">
            <button
              type="button"
              className="icon-button strong"
              onClick={handleSave}
              disabled={saving || !hasYaml}
              title="保存项目"
            >
              {saving ? <span className="spinner" /> : <Save className="h-4 w-4" aria-hidden="true" />}
              <span>保存</span>
            </button>
            <button
              type="button"
              className="icon-button"
              onClick={handleSaveAs}
              disabled={saving || !hasYaml}
              title="另存为项目"
            >
              <CopyPlus className="h-4 w-4" aria-hidden="true" />
              <span>另存为</span>
            </button>
            <ExportPanel
              disabled={!currentProject || exporting !== null}
              exporting={exporting}
              onExport={handleExport}
            />
          </div>
        </div>
      </header>

      <main className="workspace">
        <ProjectSidebar
          projects={projects}
          currentProjectId={currentProjectId}
          loading={projectLoading}
          onRefresh={loadProjects}
          onOpen={handleOpenProject}
          onDelete={handleDeleteProject}
          onNew={handleNewProject}
        />

        <div className="left-column">
          <NovelInput
            title={title}
            genre={genre}
            content={content}
            onTitleChange={handleTitleChange}
            onGenreChange={handleGenreChange}
            onContentChange={handleContentChange}
            onFileLoaded={handleFileLoaded}
            onFileError={(message) => setStatus({ tone: "error", message })}
            onClear={handleClear}
          />
        </div>

        <div className="middle-column">
          <StatusBanner tone={status.tone} message={status.message} />
          <GenerationPanel
            canParse={canParse}
            canGenerate={canGenerate}
            parsing={parsing}
            generating={generating}
            validating={validating}
            chapterCount={parseResult?.chapter_count ?? 0}
            generationMode={generationMode}
            onParse={handleParse}
            onGenerate={handleGenerate}
          />
          <ChapterList result={parseResult} />
        </div>

        <div className="right-column">
          <YamlEditor
            title={title}
            yamlText={yamlText}
            validation={validation}
            validating={validating}
            onYamlChange={handleYamlChange}
            onValidate={handleValidate}
          />
          <VersionHistory
            versions={versions}
            hasProject={Boolean(currentProject)}
            loading={versionLoading}
            onCreateVersion={handleCreateVersion}
            onRestoreVersion={handleRestoreVersion}
          />
        </div>
      </main>

      <SaveProjectDialog
        open={saveDialogMode !== null}
        initialTitle={title || "未命名项目"}
        initialGenre={genre || "未分类"}
        mode={saveDialogMode ?? "create"}
        onClose={() => setSaveDialogMode(null)}
        onSubmit={handleSaveDialogSubmit}
      />
    </div>
  );
}

export default App;
