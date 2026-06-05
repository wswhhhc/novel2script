import { Upload } from "lucide-react";
import { useRef } from "react";

interface FileUploadProps {
  onLoaded: (content: string, fileName: string) => void;
  onError: (message: string) => void;
}

const maxFileSize = Number(import.meta.env.VITE_MAX_FILE_SIZE ?? 10 * 1024 * 1024);
const supportedFormats = (import.meta.env.VITE_SUPPORTED_FORMATS ?? ".txt,.md")
  .split(",")
  .map((item: string) => item.trim().toLowerCase())
  .filter(Boolean);

export function FileUpload({ onLoaded, onError }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  function handleFile(file: File) {
    const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

    if (!supportedFormats.includes(extension)) {
      onError(`仅支持 ${supportedFormats.join("、")} 文件`);
      return;
    }

    if (file.size > maxFileSize) {
      onError(`文件不能超过 ${Math.round(maxFileSize / 1024 / 1024)}MB`);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => onLoaded(String(reader.result ?? ""), file.name);
    reader.onerror = () => onError("文件读取失败，请重试");
    reader.readAsText(file, "utf-8");
  }

  return (
    <div className="file-upload">
      <input
        ref={inputRef}
        className="sr-only"
        type="file"
        accept={supportedFormats.join(",")}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            handleFile(file);
          }
          event.target.value = "";
        }}
      />
      <button type="button" className="secondary-button w-full justify-center" onClick={() => inputRef.current?.click()}>
        <Upload className="h-4 w-4" aria-hidden="true" />
        上传 TXT / MD
      </button>
      <p className="micro-copy">最大 {Math.round(maxFileSize / 1024 / 1024)}MB，读取后会填入正文。</p>
    </div>
  );
}
