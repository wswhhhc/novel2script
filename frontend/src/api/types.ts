export interface Chapter {
  id: string;
  title: string;
  content: string;
  word_count: number;
}

export interface ParseChaptersResponse {
  chapter_count: number;
  valid: boolean;
  message: string;
  warnings: string[];
  chapters: Chapter[];
}

export interface ValidationResponse {
  valid: boolean;
  errors: string[];
}

export interface GenerateScriptResponse {
  yaml: string;
  validation: ValidationResponse;
}

export interface GenerationModeResponse {
  mode: "mock" | "ai";
  ai_enabled: boolean;
  provider: string;
  model: string;
  base_url_configured: boolean;
  api_key_configured: boolean;
  auto_fix_attempts: number;
}

export interface HealthResponse {
  status: string;
  service: string;
}

export interface ProjectSummary {
  id: number;
  title: string;
  genre: string;
  chapter_count: number;
  generation_mode: "mock" | "ai";
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail extends ProjectSummary {
  source_content: string;
  chapters: Chapter[];
  current_yaml: string;
  validation: ValidationResponse;
}

export interface ProjectPayload {
  title: string;
  genre: string;
  source_content: string;
  chapters: Chapter[];
  yaml: string;
  validation: ValidationResponse | null;
  generation_mode: "mock" | "ai";
}

export type ProjectUpdatePayload = Partial<ProjectPayload>;

export interface DeleteProjectResponse {
  message: string;
  id: number;
}

export interface ScriptVersionSummary {
  id: number;
  project_id: number;
  version_name: string;
  note: string;
  created_at: string;
}

export interface ScriptVersionDetail extends ScriptVersionSummary {
  yaml: string;
  validation: ValidationResponse;
}

export interface ScriptVersionPayload {
  version_name: string;
  yaml: string;
  validation: ValidationResponse | null;
  note: string;
}

export interface RestoreVersionResponse extends ProjectDetail {
  restored_from_version: number;
}

export type ExportFormat = "yaml" | "json" | "markdown";
