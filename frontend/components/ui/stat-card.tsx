import type { LucideIcon } from "lucide-react";

export function StatCard({
  icon: Icon,
  label,
  value,
  hint,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
          <Icon size={18} strokeWidth={2} />
        </div>
        <div className="min-w-0">
          <p className="truncate text-xl font-semibold text-zinc-900 dark:text-zinc-50">{value}</p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">{label}</p>
        </div>
      </div>
      {hint && <p className="mt-2 text-xs text-zinc-400">{hint}</p>}
    </div>
  );
}
