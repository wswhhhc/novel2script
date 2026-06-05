import { CheckCircle2, ShieldAlert } from "lucide-react";
import type { ValidationResponse } from "../api/types";

interface ValidationPanelProps {
  validation: ValidationResponse | null;
  localSyntaxError: string | null;
}

export function ValidationPanel({ validation, localSyntaxError }: ValidationPanelProps) {
  if (localSyntaxError) {
    return (
      <div className="validation-panel invalid">
        <div className="validation-title">
          <ShieldAlert className="h-4 w-4" aria-hidden="true" />
          <strong>本地语法检查失败</strong>
        </div>
        <p>{localSyntaxError}</p>
      </div>
    );
  }

  if (!validation) {
    return (
      <div className="validation-panel neutral">
        <div className="validation-title">
          <ShieldAlert className="h-4 w-4" aria-hidden="true" />
          <strong>等待校验</strong>
        </div>
        <p>生成或编辑 YAML 后，可调用后端重新校验。</p>
      </div>
    );
  }

  if (validation.valid) {
    return (
      <div className="validation-panel valid">
        <div className="validation-title">
          <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
          <strong>Schema 校验通过</strong>
        </div>
        <p>当前 YAML 符合后端校验规则。</p>
      </div>
    );
  }

  return (
    <div className="validation-panel invalid">
      <div className="validation-title">
        <ShieldAlert className="h-4 w-4" aria-hidden="true" />
        <strong>Schema 校验失败</strong>
      </div>
      <ul>
        {validation.errors.map((error) => (
          <li key={error}>{error}</li>
        ))}
      </ul>
    </div>
  );
}
