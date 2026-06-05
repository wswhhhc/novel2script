import { FileCode2, ScanText } from "lucide-react";
import type { GenerationModeResponse } from "../api/types";

const generationSteps = [
  { label: "分析章节内容", percent: 30 },
  { label: "生成角色表和场景", percent: 60 },
  { label: "生成完整剧本", percent: 90 },
  { label: "校验和修复", percent: 100 },
];

interface GenerationPanelProps {
  canParse: boolean;
  canGenerate: boolean;
  parsing: boolean;
  generating: boolean;
  validating: boolean;
  chapterCount: number;
  generationMode: GenerationModeResponse | null;
  onParse: () => void;
  onGenerate: () => void;
}

export function GenerationPanel({
  canParse,
  canGenerate,
  parsing,
  generating,
  validating,
  chapterCount,
  generationMode,
  onParse,
  onGenerate,
}: GenerationPanelProps) {
  const generationProgress = generating ? 60 : validating ? 100 : 0;
  const modeLabel = generationMode?.mode === "ai" ? "AI 模式" : generationMode?.mode === "mock" ? "Mock 模式" : "模式未知";
  const modeClass = generationMode?.mode === "ai" ? "ai" : "neutral";

  return (
    <section className="workspace-panel compact-panel">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">执行</p>
          <h2>生成链路</h2>
        </div>
        <div className="badge-group">
          <span className={`badge ${modeClass}`}>{modeLabel}</span>
          <span className="badge neutral">{chapterCount ? `${chapterCount} 章` : "待识别"}</span>
        </div>
      </div>

      <div className="action-stack">
        <button type="button" className="primary-button" onClick={onParse} disabled={!canParse || parsing || generating}>
          {parsing ? <span className="spinner" /> : <ScanText className="h-4 w-4" aria-hidden="true" />}
          {parsing ? "正在识别章节" : "识别章节"}
        </button>

        <button type="button" className="primary-button dark" onClick={onGenerate} disabled={!canGenerate || generating || parsing}>
          {generating ? <span className="spinner light" /> : <FileCode2 className="h-4 w-4" aria-hidden="true" />}
          {generating ? "正在生成 YAML 剧本" : "生成剧本"}
        </button>
      </div>

      {generating || validating ? (
        <div className="generation-progress" aria-label="生成进度">
          <div className="progress-head">
            <span>{generating ? "正在生成" : "正在校验"}</span>
            <strong>{generationProgress}%</strong>
          </div>
          <div className="progress-track">
            <div style={{ width: `${generationProgress}%` }} />
          </div>
        </div>
      ) : null}

      <div className="process-list">
        <div className={parsing ? "active" : canParse ? "ready" : ""}>
          <span>1</span>
          <p>解析章节边界和字数</p>
        </div>
        <div className={generating ? "active" : canGenerate ? "ready" : ""}>
          <span>2</span>
          <p>{generationMode?.mode === "mock" ? "Mock 生成剧本" : "AI 生成剧本（5 阶段）"}</p>
          {generating ? (
            <div className="substeps">
              {generationSteps.map((step) => (
                <small key={step.label}>
                  <b>{step.percent}%</b>
                  {step.label}
                </small>
              ))}
            </div>
          ) : null}
        </div>
        <div className={validating ? "active" : ""}>
          <span>3</span>
          <p>重新校验 YAML Schema</p>
        </div>
      </div>
    </section>
  );
}
