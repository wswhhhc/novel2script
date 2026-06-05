import yaml from "js-yaml";

export function getYamlSyntaxError(value: string) {
  if (!value.trim()) {
    return null;
  }

  try {
    yaml.load(value);
    return null;
  } catch (error) {
    return error instanceof Error ? error.message : "YAML 语法无法解析";
  }
}
