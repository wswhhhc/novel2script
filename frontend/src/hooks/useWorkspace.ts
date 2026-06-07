import { useEffect, useMemo, useState } from "react";
import { generateScriptStream, getGenerationMode, parseChapters, validateYaml } from "../api/client";
import type { GenerationModeResponse, ParseChaptersResponse, ValidationResponse } from "../api/types";

export interface WorkspaceState {
  title: string;
  genre: string;
  content: string;
  parseResult: ParseChaptersResponse | null;
  yamlText: string;
  validation: ValidationResponse | null;
  dirty: boolean;
}

export interface WorkspaceInternal {
  setTitle: (v: string) => void;
  setGenre: (v: string) => void;
  setContent: (v: string) => void;
  setParseResult: (v: ParseChaptersResponse | null) => void;
  setYamlText: (v: string) => void;
  setValidation: (v: ValidationResponse | null) => void;
  setDirty: (v: boolean) => void;
  setStatus: (s: { tone: string; message: string }) => void;
}

export interface WorkspaceActions {
  canParse: boolean;
  canGenerate: boolean;
  hasYaml: boolean;
  totalWords: number;
  parsing: boolean;
  generating: boolean;
  generationProgress: number;
  generationMessage: string;
  validating: boolean;
  generationMode: GenerationModeResponse | null;
  handleParse: () => Promise<void>;
  handleGenerate: () => Promise<void>;
  handleValidate: () => Promise<void>;
  handleFileLoaded: (fileContent: string, fileName: string) => void;
  handleTitleChange: (value: string) => void;
  handleGenreChange: (value: string) => void;
  handleContentChange: (value: string) => void;
  handleYamlChange: (value: string) => void;
  handleClear: () => void;
  status: { tone: string; message: string };
  setStatus: (status: { tone: "info" | "success" | "warning" | "error"; message: string }) => void;
}

export function useWorkspace() {
  const [title, setTitle] = useState("");
  const [genre, setGenre] = useState("悬疑");
  const [content, setContent] = useState("");
  const [parseResult, setParseResult] = useState<ParseChaptersResponse | null>(null);
  const [yamlText, setYamlText] = useState("");
  const [validation, setValidation] = useState<ValidationResponse | null>(null);
  const [status, setStatus] = useState<{ tone: "info" | "success" | "warning" | "error"; message: string }>({
    tone: "info",
    message: "粘贴小说正文或上传文件后开始识别章节。",
  });
  const [generationMode, setGenerationMode] = useState<GenerationModeResponse | null>(null);
  const [dirty, setDirty] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationMessage, setGenerationMessage] = useState("");
  const [validating, setValidating] = useState(false);

  const canParse = content.trim().length > 0;
  const canGenerate = Boolean(parseResult?.valid && parseResult.chapter_count >= 3 && parseResult.chapters.length >= 3);
  const hasYaml = yamlText.trim().length > 0;

  const totalWords = useMemo(
    () => parseResult?.chapters.reduce((sum, chapter) => sum + chapter.word_count, 0) ?? 0,
    [parseResult]
  );

  useEffect(() => {
    let mounted = true;
    getGenerationMode()
      .then((mode) => {
        if (mounted) setGenerationMode(mode);
      })
      .catch(() => {
        if (mounted) setGenerationMode(null);
      });
    return () => {
      mounted = false;
    };
  }, []);

  async function handleParse() {
    if (!canParse || parsing) return;

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
    if (!canGenerate || !parseResult || generating) return;

    if (!title.trim()) {
      setStatus({ tone: "warning", message: "生成剧本前请填写小说标题。" });
      return;
    }

    setGenerating(true);
    setGenerationProgress(5);
    setGenerationMessage("正在准备流式生成 YAML 剧本...");
    setYamlText("");
    setValidation(null);
    setStatus({ tone: "info", message: "正在准备流式生成 YAML 剧本..." });

    try {
      await generateScriptStream(title.trim(), genre.trim() || "未分类", parseResult.chapters, (event) => {
        if ("progress" in event && typeof event.progress === "number") {
          setGenerationProgress(event.progress);
        }

        if (event.type === "status") {
          setGenerationMessage(event.message);
          setStatus({ tone: "info", message: event.message });
          return;
        }

        if (event.type === "yaml_delta") {
          setYamlText((current) => current + event.delta);
          setValidation(null);
          setDirty(true);
          return;
        }

        if (event.type === "validation") {
          setValidation(event.validation);
          return;
        }

        if (event.type === "done") {
          setYamlText(event.yaml);
          setValidation(event.validation);
          setDirty(true);
          setGenerationProgress(100);
          setGenerationMessage(event.message ?? "剧本生成完成。");
          setStatus({
            tone: event.validation.valid ? "success" : "warning",
            message:
              event.message ??
              (event.validation.valid ? "剧本生成成功，Schema 校验通过。" : "剧本生成成功，但 Schema 校验有错误。"),
          });
          return;
        }

        if (event.type === "error") {
          throw new Error(event.message);
        }
      });
    } catch (error) {
      setStatus({ tone: "error", message: error instanceof Error ? error.message : "剧本生成请求失败" });
    } finally {
      setGenerating(false);
      setGenerationProgress(0);
      setGenerationMessage("");
    }
  }

  async function handleValidate() {
    if (!hasYaml || validating) return;

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

  function handleClear() {
    handleNewProject();
  }

  function handleNewProject() {
    setTitle("");
    setGenre("悬疑");
    setContent("");
    setParseResult(null);
    setYamlText("");
    setValidation(null);
    setDirty(false);
    setStatus({ tone: "info", message: "已清空输入内容。" });
  }

  return {
    title,
    genre,
    content,
    parseResult,
    yamlText,
    validation,
    dirty,
    canParse,
    canGenerate,
    hasYaml,
    totalWords,
    parsing,
    generating,
    generationProgress,
    generationMessage,
    validating,
    generationMode,
    status,
    setStatus,
    handleParse,
    handleGenerate,
    handleValidate,
    handleFileLoaded,
    handleTitleChange,
    handleGenreChange,
    handleContentChange,
    handleYamlChange,
    handleClear,
    _internal: { setTitle, setGenre, setContent, setParseResult, setYamlText, setValidation, setDirty, setStatus },
  } as WorkspaceActions & WorkspaceState & { _internal: WorkspaceInternal };
}
