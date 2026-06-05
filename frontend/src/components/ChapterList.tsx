import { ChevronDown, ListChecks } from "lucide-react";
import type { ParseChaptersResponse } from "../api/types";
import { StatusBanner } from "./StatusBanner";

interface ChapterListProps {
  result: ParseChaptersResponse | null;
}

export function ChapterList({ result }: ChapterListProps) {
  if (!result) {
    return (
      <section className="workspace-panel">
        <div className="panel-head">
          <div>
            <p className="panel-kicker">章节</p>
            <h2>识别结果</h2>
          </div>
          <span className="badge neutral">未识别</span>
        </div>
        <div className="empty-state">
          <ListChecks className="h-6 w-6" aria-hidden="true" />
          <p>输入小说正文后，先识别章节再生成剧本。</p>
        </div>
      </section>
    );
  }

  return (
    <section className="workspace-panel">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">章节</p>
          <h2>识别结果</h2>
        </div>
        <span className={`badge ${result.valid ? "success" : "error"}`}>
          {result.valid ? "可生成" : "需处理"}
        </span>
      </div>

      <StatusBanner tone={result.valid ? "success" : "error"} message={result.message} />

      {result.warnings.length > 0 ? (
        <div className="warning-stack">
          {result.warnings.map((warning) => (
            <StatusBanner key={warning} tone="warning" message={warning} />
          ))}
        </div>
      ) : null}

      <div className="chapter-summary">
        <div>
          <span className="metric-label">章节数</span>
          <strong>{result.chapter_count}</strong>
        </div>
        <div>
          <span className="metric-label">总字数</span>
          <strong>{result.chapters.reduce((sum, chapter) => sum + chapter.word_count, 0).toLocaleString()}</strong>
        </div>
      </div>

      <div className="chapter-list">
        {result.chapters.map((chapter) => (
          <details key={chapter.id} className="chapter-item">
            <summary>
              <div>
                <span className="chapter-id">{chapter.id}</span>
                <strong>{chapter.title}</strong>
              </div>
              <span className="chapter-count">{chapter.word_count.toLocaleString()} 字</span>
              <ChevronDown className="summary-icon h-4 w-4" aria-hidden="true" />
            </summary>
            <p>{chapter.content.slice(0, 260)}{chapter.content.length > 260 ? "..." : ""}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
