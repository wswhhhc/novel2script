import { AlertCircle, CheckCircle2, Info, TriangleAlert } from "lucide-react";

export type BannerTone = "info" | "success" | "warning" | "error";

interface StatusBannerProps {
  tone: BannerTone;
  message: string;
}

const iconMap = {
  info: Info,
  success: CheckCircle2,
  warning: TriangleAlert,
  error: AlertCircle,
};

export function StatusBanner({ tone, message }: StatusBannerProps) {
  const Icon = iconMap[tone];

  return (
    <div className={`status-banner status-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </div>
  );
}
