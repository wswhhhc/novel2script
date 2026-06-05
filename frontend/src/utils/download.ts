export function downloadTextFile(content: string, fileName: string, mimeType = "text/yaml;charset=utf-8") {
  const blob = new Blob([content], { type: mimeType });
  downloadBlob(blob, fileName);
}

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

export function buildYamlFileName(title: string) {
  const normalized = title.trim().replace(/[\\/:*?"<>|]+/g, "-").replace(/\s+/g, "-");
  const stamp = new Date().toISOString().slice(0, 10);
  return `${normalized || "novel2script"}-${stamp}.yaml`;
}
