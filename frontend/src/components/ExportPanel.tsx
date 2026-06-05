import { Download } from "lucide-react";
import type { ExportFormat } from "../api/types";

interface ExportPanelProps {
  disabled: boolean;
  exporting: ExportFormat | null;
  onExport: (format: ExportFormat) => void;
}

const formats: Array<{ label: string; value: ExportFormat }> = [
  { label: "YAML", value: "yaml" },
  { label: "JSON", value: "json" },
  { label: "Markdown", value: "markdown" },
];

export function ExportPanel({ disabled, exporting, onExport }: ExportPanelProps) {
  return (
    <div className="export-strip">
      {formats.map((format) => (
        <button
          key={format.value}
          type="button"
          className="icon-button"
          onClick={() => onExport(format.value)}
          disabled={disabled || exporting !== null}
          title={`导出 ${format.label}`}
        >
          {exporting === format.value ? (
            <span className="spinner" />
          ) : (
            <Download className="h-4 w-4" aria-hidden="true" />
          )}
          <span>{format.label}</span>
        </button>
      ))}
    </div>
  );
}
