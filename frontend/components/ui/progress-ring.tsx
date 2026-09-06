/** Circular 0-100 score visualization — the dashboard's centerpiece stat.
 * Same color thresholds as ScoreBar for consistency across the app. */
export function ProgressRing({
  score,
  size = 96,
  strokeWidth = 8,
  label,
}: {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? "stroke-emerald-500" : score >= 40 ? "stroke-amber-500" : "stroke-red-500";

  return (
    <div className="relative inline-flex shrink-0 items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          className="fill-none stroke-zinc-100 dark:stroke-zinc-800"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={`fill-none ${color} transition-[stroke-dashoffset] duration-700 ease-out`}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">{score}%</span>
        {label && <span className="text-[10px] text-zinc-400">{label}</span>}
      </div>
    </div>
  );
}
