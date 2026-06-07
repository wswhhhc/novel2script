import { useState } from "react";
import {
  createProject,
  createVersion,
  deleteProject,
  exportProject,
  getProject,
  listProjects,
  listVersions,
  restoreVersion,
  updateProject,
} from "../api/client";
import type {
  ExportFormat,
  ParseChaptersResponse,
  ProjectDetail,
  ProjectPayload,
  ProjectSummary,
  ScriptVersionSummary,
  ValidationResponse,
} from "../api/types";
import { downloadBlob } from "../utils/download";

export interface ProjectWorkspaceBridge {
  title: string;
  genre: string;
  content: string;
  yamlText: string;
  parseResult: ParseChaptersResponse | null;
  validation: ValidationResponse | null;
  generationMode: "mock" | "ai" | undefined;
  dirty: boolean;
  applyProject: (p: ProjectDetail) => void;
  resetWorkspace: (msg?: string) => void;
  setStatus: (s: { tone: string; message: string }) => void;
}

export function useProjects(bridge: ProjectWorkspaceBridge) {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [currentProject, setCurrentProject] = useState<ProjectDetail | null>(null);
  const [versions, setVersions] = useState<ScriptVersionSummary[]>([]);
  const [projectLoading, setProjectLoading] = useState(false);
  const [versionLoading, setVersionLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [exporting, setExporting] = useState<ExportFormat | null>(null);
  const [saveDialogMode, setSaveDialogMode] = useState<"create" | "copy" | null>(null);

  const currentProjectId = currentProject?.id ?? null;

  function buildPayload(nextTitle: string, nextGenre: string): ProjectPayload {
    return {
      title: nextTitle.trim(),
      genre: nextGenre.trim() || "未分类",
      source_content: bridge.content,
      chapters: bridge.parseResult?.chapters ?? [],
      yaml: bridge.yamlText,
      validation: bridge.validation,
      generation_mode: bridge.generationMode ?? currentProject?.generation_mode ?? "mock",
    };
  }

  function doApplyProject(project: ProjectDetail) {
    setCurrentProject(project);
    setVersions([]);
    bridge.applyProject(project);
  }

  function doResetWorkspace(message = "已清空输入内容。") {
    setCurrentProject(null);
    setVersions([]);
    bridge.resetWorkspace(message);
  }

  async function loadProjects() {
    setProjectLoading(true);
    try {
      setProjects(await listProjects());
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目列表加载失败" });
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
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本历史加载失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleOpenProject(projectId: number) {
    if (bridge.dirty && currentProjectId !== projectId && !window.confirm("当前内容有未保存修改，确定打开其他项目吗？")) {
      return;
    }

    setProjectLoading(true);
    try {
      const project = await getProject(projectId);
      doApplyProject(project);
      await loadVersions(project.id);
      bridge.setStatus({ tone: "success", message: `已打开项目：${project.title}` });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目打开失败" });
    } finally {
      setProjectLoading(false);
    }
  }

  async function handleDeleteProject(projectId: number) {
    if (!window.confirm("删除后无法恢复，确定删除这个项目吗？")) return;

    try {
      await deleteProject(projectId);
      await loadProjects();
      if (currentProjectId === projectId) {
        doResetWorkspace("当前项目已删除。");
      } else {
        bridge.setStatus({ tone: "success", message: "项目已删除。" });
      }
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目删除失败" });
    }
  }

  async function handleSave() {
    if (!bridge.yamlText.trim()) {
      bridge.setStatus({ tone: "warning", message: "请先生成或填写 YAML 剧本，再保存项目。" });
      return;
    }
    if (!bridge.content.trim()) {
      bridge.setStatus({ tone: "warning", message: "保存项目前需要保留小说正文。" });
      return;
    }
    if (!currentProject) {
      setSaveDialogMode("create");
      return;
    }
    await saveExistingProject();
  }

  async function handleSaveAs() {
    if (!bridge.yamlText.trim() || !bridge.content.trim()) {
      bridge.setStatus({ tone: "warning", message: "另存为前需要小说正文和 YAML 剧本。" });
      return;
    }
    setSaveDialogMode("copy");
  }

  async function saveExistingProject() {
    if (!currentProject) return;

    setSaving(true);
    bridge.setStatus({ tone: "info", message: "正在保存项目..." });
    try {
      const project = await updateProject(currentProject.id, buildPayload(bridge.title, bridge.genre));
      doApplyProject(project);
      await loadProjects();
      bridge.setStatus({ tone: project.validation.valid ? "success" : "warning", message: "项目已保存。" });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目保存失败" });
    } finally {
      setSaving(false);
    }
  }

  async function handleSaveDialogSubmit(nextTitle: string, nextGenre: string) {
    setSaveDialogMode(null);
    await createNewProject(nextTitle, nextGenre);
  }

  async function createNewProject(nextTitle: string, nextGenre: string) {
    setSaving(true);
    bridge.setStatus({ tone: "info", message: "正在创建项目..." });
    try {
      const summary = await createProject(buildPayload(nextTitle, nextGenre));
      const project = await getProject(summary.id);
      doApplyProject(project);
      await loadProjects();
      await loadVersions(project.id);
      bridge.setStatus({
        tone: project.validation.valid ? "success" : "warning",
        message: `项目已保存：${project.title}`,
      });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "项目创建失败" });
    } finally {
      setSaving(false);
    }
  }

  async function handleCreateVersion() {
    if (!currentProject) {
      bridge.setStatus({ tone: "warning", message: "请先保存项目，再创建版本快照。" });
      return;
    }
    if (!bridge.yamlText.trim()) {
      bridge.setStatus({ tone: "warning", message: "YAML 为空，不能创建版本快照。" });
      return;
    }

    const versionName = window.prompt("请输入版本名称", `版本 ${versions.length + 1}`);
    if (!versionName?.trim()) return;
    const note = window.prompt("版本说明（可选）", "") ?? "";

    setVersionLoading(true);
    try {
      await createVersion(currentProject.id, {
        version_name: versionName.trim(),
        yaml: bridge.yamlText,
        validation: bridge.validation,
        note,
      });
      await loadVersions(currentProject.id);
      bridge.setStatus({ tone: "success", message: `已保存版本：${versionName.trim()}` });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本保存失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleRestoreVersion(version: ScriptVersionSummary) {
    if (!currentProject || !window.confirm(`确定恢复到版本"${version.version_name}"吗？当前 YAML 会被覆盖。`)) {
      return;
    }

    setVersionLoading(true);
    try {
      const project = await restoreVersion(currentProject.id, version.id);
      doApplyProject(project);
      await loadProjects();
      await loadVersions(project.id);
      bridge.setStatus({
        tone: project.validation.valid ? "success" : "warning",
        message: `已恢复到版本：${version.version_name}`,
      });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "版本恢复失败" });
    } finally {
      setVersionLoading(false);
    }
  }

  async function handleExport(format: ExportFormat) {
    if (!currentProject) {
      bridge.setStatus({ tone: "warning", message: "请先保存项目，再使用后端导出。" });
      return;
    }

    setExporting(format);
    try {
      const result = await exportProject(currentProject.id, format);
      downloadBlob(result.blob, result.filename);
      bridge.setStatus({ tone: "success", message: `已导出 ${format === "markdown" ? "Markdown" : format.toUpperCase()}。` });
    } catch (error) {
      bridge.setStatus({ tone: "error", message: error instanceof Error ? error.message : "导出失败" });
    } finally {
      setExporting(null);
    }
  }

  function handleNewProject() {
    if (bridge.dirty && !window.confirm("当前内容有未保存修改，确定新建项目吗？")) return;
    doResetWorkspace("已新建空白项目。");
  }

  return {
    projects,
    currentProject,
    currentProjectId,
    versions,
    projectLoading,
    versionLoading,
    saving,
    exporting,
    saveDialogMode,
    setSaveDialogMode,
    loadProjects,
    handleOpenProject,
    handleDeleteProject,
    handleSave,
    handleSaveAs,
    handleCreateVersion,
    handleRestoreVersion,
    handleExport,
    handleNewProject,
    handleSaveDialogSubmit,
  };
}
