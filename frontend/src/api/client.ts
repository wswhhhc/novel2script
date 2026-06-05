import type {
  Chapter,
  GenerateScriptResponse,
  GenerationModeResponse,
  HealthResponse,
  ParseChaptersResponse,
  DeleteProjectResponse,
  ExportFormat,
  ProjectDetail,
  ProjectPayload,
  ProjectSummary,
  ProjectUpdatePayload,
  RestoreVersionResponse,
  ScriptVersionPayload,
  ScriptVersionSummary,
  ValidationResponse,
} from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    throw new Error(extractErrorMessage(data, response.statusText));
  }

  return data as T;
}

function extractErrorMessage(data: unknown, fallback: string): string {
  if (typeof data === "string" && data.trim()) {
    return data;
  }

  if (data && typeof data === "object") {
    const detail = (data as { detail?: unknown; message?: unknown }).detail;
    const message = (data as { message?: unknown }).message;

    if (typeof message === "string") {
      return message;
    }

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }
          return String(item);
        })
        .join("；");
    }
  }

  return fallback || "请求失败";
}

export function checkHealth() {
  return request<HealthResponse>("/health");
}

export function getGenerationMode() {
  return request<GenerationModeResponse>("/api/script/mode");
}

export function parseChapters(content: string) {
  return request<ParseChaptersResponse>("/api/chapters/parse", {
    method: "POST",
    body: JSON.stringify({ content }),
  });
}

export function validateYaml(yaml: string) {
  return request<ValidationResponse>("/api/script/validate", {
    method: "POST",
    body: JSON.stringify({ yaml }),
  });
}

export function generateScript(title: string, genre: string, chapters: Chapter[]) {
  return request<GenerateScriptResponse>("/api/script/generate", {
    method: "POST",
    body: JSON.stringify({ title, genre, chapters }),
  });
}

export function listProjects() {
  return request<ProjectSummary[]>("/api/projects");
}

export function createProject(payload: ProjectPayload) {
  return request<ProjectSummary>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getProject(id: number) {
  return request<ProjectDetail>(`/api/projects/${id}`);
}

export function updateProject(id: number, payload: ProjectUpdatePayload) {
  return request<ProjectDetail>(`/api/projects/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteProject(id: number) {
  return request<DeleteProjectResponse>(`/api/projects/${id}`, {
    method: "DELETE",
  });
}

export function createVersion(projectId: number, payload: ScriptVersionPayload) {
  return request<ScriptVersionSummary>(`/api/projects/${projectId}/versions`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listVersions(projectId: number) {
  return request<ScriptVersionSummary[]>(`/api/projects/${projectId}/versions`);
}

export function restoreVersion(projectId: number, versionId: number) {
  return request<RestoreVersionResponse>(`/api/projects/${projectId}/versions/${versionId}/restore`, {
    method: "POST",
  });
}

export async function exportProject(projectId: number, format: ExportFormat) {
  const response = await fetch(`${API_BASE_URL}/api/projects/${projectId}/export/${format}`);

  if (!response.ok) {
    const contentType = response.headers.get("content-type") ?? "";
    const data = contentType.includes("application/json") ? await response.json() : await response.text();
    throw new Error(extractErrorMessage(data, response.statusText));
  }

  const blob = await response.blob();
  return { blob, filename: extractDownloadFileName(response.headers.get("content-disposition"), format) };
}

function extractDownloadFileName(contentDisposition: string | null, format: ExportFormat) {
  const extension = format === "markdown" ? "md" : format;
  if (!contentDisposition) {
    return `novel2script_script.${extension}`;
  }

  const encodedMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
  if (encodedMatch) {
    return decodeURIComponent(encodedMatch[1]);
  }

  const fallbackMatch = contentDisposition.match(/filename="([^"]+)"/);
  return fallbackMatch?.[1] ?? `novel2script_script.${extension}`;
}
