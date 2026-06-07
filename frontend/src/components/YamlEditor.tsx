import Editor from "@monaco-editor/react";
import { Clipboard, Download, RotateCw } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { ValidationResponse } from "../api/types";
import { buildYamlFileName, downloadTextFile } from "../utils/download";
import { getYamlSyntaxError } from "../utils/yaml";
import { ValidationPanel } from "./ValidationPanel";

/** 从 HTML 根元素读取当前主题。 */
function monacoTheme() {
  return document.documentElement.dataset.theme === "dark" ? "vs-dark" : "vs";
}

interface YamlEditorProps {
  title: string;
  yamlText: string;
  validation: ValidationResponse | null;
  generating: boolean;
  validating: boolean;
  onYamlChange: (value: string) => void;
  onValidate: () => void;
}

export function YamlEditor({
  title,
  yamlText,
  validation,
  generating,
  validating,
  onYamlChange,
  onValidate,
}: YamlEditorProps) {
  const [copyState, setCopyState] = useState("复制");
  const [editorTheme, setEditorTheme] = useState(monacoTheme);
  const localSyntaxError = useMemo(() => (generating ? null : getYamlSyntaxError(yamlText)), [generating, yamlText]);
  const hasYaml = yamlText.trim().length > 0;

  // 响应 data-theme 属性变化，切换 Monaco 主题
  useEffect(() => {
    const observer = new MutationObserver(() => setEditorTheme(monacoTheme()));
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  async function handleCopy() {
    if (!hasYaml) {
      return;
    }

    await navigator.clipboard.writeText(yamlText);
    setCopyState("已复制");
    window.setTimeout(() => setCopyState("复制"), 1400);
  }

  function handleDownload() {
    if (!hasYaml) {
      return;
    }
    downloadTextFile(yamlText, buildYamlFileName(title));
  }

  return (
    <section className="workspace-panel yaml-panel">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">输出</p>
          <h2>YAML 剧本</h2>
        </div>
        <div className="toolbar">
          <button
            type="button"
            className="icon-button"
            onClick={handleCopy}
            disabled={!hasYaml}
            title="复制 YAML"
            aria-label="复制 YAML"
          >
            <Clipboard className="h-4 w-4" aria-hidden="true" />
            <span>{copyState}</span>
          </button>
          <button
            type="button"
            className="icon-button"
            onClick={handleDownload}
            disabled={!hasYaml}
            title="下载 YAML"
            aria-label="下载 YAML"
          >
            <Download className="h-4 w-4" aria-hidden="true" />
            <span>下载</span>
          </button>
          <button
            type="button"
            className="icon-button strong"
            onClick={onValidate}
            disabled={!hasYaml || generating || validating}
            title="重新校验"
            aria-label="重新校验 YAML"
          >
            {validating ? <span className="spinner" /> : <RotateCw className="h-4 w-4" aria-hidden="true" />}
            <span>{generating ? "生成中" : validating ? "校验中" : "校验"}</span>
          </button>
        </div>
      </div>

      <div className="editor-shell">
        <Editor
          height="100%"
          language="yaml"
          theme={editorTheme}
          value={yamlText}
          loading={<div className="editor-loading">编辑器加载中...</div>}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineHeight: 20,
            wordWrap: "on",
            scrollBeyondLastLine: false,
            tabSize: 2,
            padding: { top: 12, bottom: 12 },
            renderLineHighlight: "line",
          }}
          onChange={(value) => onYamlChange(value ?? "")}
        />
      </div>

      <ValidationPanel validation={validation} localSyntaxError={localSyntaxError} generating={generating} />
    </section>
  );
}
