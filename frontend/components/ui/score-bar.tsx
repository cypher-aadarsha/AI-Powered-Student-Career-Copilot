/** Shared 0-100 score visualization — used by the resume analyzer (Phase 5)
 * and career skill-gap matching (Phase 6), which both produce an
 * explainable 0-100 fit score. */
export function ScoreBar({ score }: { score: number }) {
  const color = score >= 70 ? "bg-emerald-500" : score >= 40 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-32 overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        <div className={`h-full ${color}`} style={{ width: `${score}%` }} />
      </div>
      <span className="text-sm font-medium text-zinc-700 dark:text-zinc-200">{score}/100</span>
    </div>
  );
}
