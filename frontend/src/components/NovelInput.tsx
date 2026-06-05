import { Eraser } from "lucide-react";
import { FileUpload } from "./FileUpload";

interface NovelInputProps {
  title: string;
  genre: string;
  content: string;
  onTitleChange: (value: string) => void;
  onGenreChange: (value: string) => void;
  onContentChange: (value: string) => void;
  onFileLoaded: (content: string, fileName: string) => void;
  onFileError: (message: string) => void;
  onClear: () => void;
}

const genres = ["悬疑", "都市", "古装", "科幻", "言情", "未分类"];

export function NovelInput({
  title,
  genre,
  content,
  onTitleChange,
  onGenreChange,
  onContentChange,
  onFileLoaded,
  onFileError,
  onClear,
}: NovelInputProps) {
  const charCount = content.length;

  return (
    <section className="workspace-panel">
      <div className="panel-head">
        <div>
          <p className="panel-kicker">输入</p>
          <h2>小说文本</h2>
        </div>
        <button type="button" className="ghost-button" onClick={onClear} disabled={!title && !content}>
          <Eraser className="h-4 w-4" aria-hidden="true" />
          清空
        </button>
      </div>

      <label className="field">
        <span>小说标题</span>
        <input
          value={title}
          onChange={(event) => onTitleChange(event.target.value)}
          placeholder="用于生成和下载文件名"
        />
      </label>

      <label className="field">
        <span>剧本类型</span>
        <select value={genre} onChange={(event) => onGenreChange(event.target.value)}>
          {genres.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>

      <FileUpload onLoaded={onFileLoaded} onError={onFileError} />

      <label className="field grow">
        <span>小说正文</span>
        <textarea
          className="novel-textarea"
          value={content}
          onChange={(event) => onContentChange(event.target.value)}
          placeholder="粘贴包含至少 3 个章节的小说文本，例如：第一章 ... 第二章 ... 第三章 ..."
        />
      </label>

      <div className="metric-row">
        <span>{charCount.toLocaleString()} 字</span>
        <span>{content.trim() ? "可识别章节" : "等待输入"}</span>
      </div>
    </section>
  );
}
