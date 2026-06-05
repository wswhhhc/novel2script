import { readFileSync } from "node:fs";
import { dirname } from "node:path";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");

function read(relativePath) {
  return readFileSync(resolve(root, relativePath), "utf-8");
}

function assertContains(source, expected, label) {
  if (!source.includes(expected)) {
    throw new Error(`Smoke test failed: ${label}`);
  }
}

const app = read("src/App.tsx");
const client = read("src/api/client.ts");
const generationPanel = read("src/components/GenerationPanel.tsx");
const chapterList = read("src/components/ChapterList.tsx");
const validationPanel = read("src/components/ValidationPanel.tsx");
const fileUpload = read("src/components/FileUpload.tsx");
const yamlEditor = read("src/components/YamlEditor.tsx");
const projectSidebar = read("src/components/ProjectSidebar.tsx");
const versionHistory = read("src/components/VersionHistory.tsx");
const exportPanel = read("src/components/ExportPanel.tsx");

assertContains(
  generationPanel,
  "disabled={!canGenerate || generating || parsing}",
  "generation button stays disabled while chapters are invalid"
);
assertContains(client, "getGenerationMode", "generation mode API client is present");
assertContains(app, "setGenerationMode(mode)", "generation mode is read on page load");
assertContains(generationPanel, "AI 模式", "generation mode badge is rendered");
assertContains(
  app,
  'result.warnings.length > 0 ? "warning" : "success"',
  "chapter warnings are surfaced as warning status"
);
assertContains(chapterList, 'tone="warning"', "chapter warnings render with warning style");
assertContains(validationPanel, "validation.errors.map", "schema validation errors are listed");
assertContains(app, "setValidation(null);", "editing or changing inputs resets validation without clearing YAML edits");
assertContains(yamlEditor, 'onYamlChange(value ?? "")', "YAML editor keeps user-entered content during edits");
assertContains(fileUpload, "supportedFormats.includes(extension)", "file extension validation is present");
assertContains(fileUpload, "file.size > maxFileSize", "file size validation is present");
assertContains(app, "handleSave", "save project entry is present");
assertContains(projectSidebar, "本地项目", "project list entry is present");
assertContains(versionHistory, "版本历史", "version history entry is present");
assertContains(exportPanel, "YAML", "YAML export entry is present");
assertContains(exportPanel, "JSON", "JSON export entry is present");
assertContains(exportPanel, "Markdown", "Markdown export entry is present");
assertContains(client, "exportProject", "project export API client is present");
assertContains(client, "restoreVersion", "version restore API client is present");

console.log("Frontend smoke checks passed.");
