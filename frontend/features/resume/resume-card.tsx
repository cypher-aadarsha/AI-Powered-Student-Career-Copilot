"use client";

import { useState } from "react";

import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { ScoreBar } from "@/components/ui/score-bar";
import type { Resume, ResumeStatus } from "@/types/resume";
import { resumeApi } from "./api";

const statusLabel: Record<ResumeStatus, string> = {
  uploaded: "Uploaded",
  parsing: "Parsing…",
  parsed: "Parsed",
  failed: "Failed",
};

const statusColor: Record<ResumeStatus, string> = {
  uploaded: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300",
  parsing: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400",
  parsed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400",
  failed: "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400",
};

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function BulletList({ label, items }: { label: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div>
      <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">{label}</p>
      <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm text-zinc-600 dark:text-zinc-300">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function ResumeCard({ resume, onChange }: { resume: Resume; onChange: () => void }) {
  const [isReanalyzing, setIsReanalyzing] = useState(false);

  return (
    <li className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{resume.original_filename}</h3>
          <p className="text-xs text-zinc-400">
            {formatSize(resume.file_size_bytes)} · uploaded {new Date(resume.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColor[resume.status]}`}>
            {statusLabel[resume.status]}
          </span>
          {resume.status === "parsed" && (
            <button
              type="button"
              disabled={isReanalyzing}
              onClick={async () => {
                setIsReanalyzing(true);
                try {
                  await resumeApi.reanalyze(resume.id);
                  onChange();
                } finally {
                  setIsReanalyzing(false);
                }
              }}
              className="text-xs font-medium text-zinc-400 hover:text-zinc-700 disabled:opacity-60 dark:hover:text-zinc-200"
            >
              {isReanalyzing ? "Re-analyzing…" : "Re-analyze"}
            </button>
          )}
          <InlineConfirmButton
            onConfirm={async () => {
              await resumeApi.remove(resume.id);
              onChange();
            }}
          />
        </div>
      </div>

      {resume.status === "failed" && resume.parse_error && (
        <p className="mt-3 text-sm text-red-600 dark:text-red-400">{resume.parse_error}</p>
      )}

      {resume.status === "parsed" && (
        <div className="mt-4 flex flex-col gap-4">
          {resume.ai_score !== null && <ScoreBar score={resume.ai_score} />}
          {resume.ai_summary && <p className="text-sm text-zinc-600 dark:text-zinc-300">{resume.ai_summary}</p>}

          {resume.parsed_data && resume.parsed_data.detected_skills.length > 0 && (
            <div>
              <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Detected skills</p>
              <div className="mt-1 flex flex-wrap gap-1.5">
                {resume.parsed_data.detected_skills.map((skill) => (
                  <span
                    key={skill}
                    className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          <BulletList label="Strengths" items={resume.ai_strengths ?? []} />
          <BulletList label="Suggestions" items={resume.ai_suggestions ?? []} />
        </div>
      )}
    </li>
  );
}
