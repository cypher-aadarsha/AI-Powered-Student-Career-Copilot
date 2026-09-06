"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SectionCard } from "@/components/layout/section-card";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { jobApi } from "@/features/job/api";
import { ApiError } from "@/lib/api-client";
import type { JobDetail } from "@/types/job";

const employmentLabel: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  internship: "Internship",
  contract: "Contract",
};

export default function JobDetailPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<JobDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await jobApi.get(params.id);
        if (!cancelled) setDetail(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Could not load this job.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user, params.id]);

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  if (error || !detail) {
    return (
      <div className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-sm rounded-lg bg-red-50 px-4 py-3 text-center text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
          {error ?? "Job not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <Link href="/jobs" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
          ← All jobs
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{detail.job.title}</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          {detail.job.company} · {detail.job.location} · {employmentLabel[detail.job.employment_type]}
          {detail.job.is_remote && " · Remote"}
        </p>
        {detail.description && <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{detail.description}</p>}
        <a
          href={detail.apply_url}
          target="_blank"
          rel="noreferrer"
          className="mt-3 inline-block rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-zinc-50 hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          Apply
        </a>
      </div>

      <SectionCard title="Your fit">
        <div className="flex flex-col gap-4">
          <ScoreBar score={detail.score} />
          <p className="text-sm text-zinc-600 dark:text-zinc-300">{detail.summary}</p>
        </div>
      </SectionCard>

      {detail.matched_skills.length > 0 && (
        <SectionCard title="Skills you have">
          <div className="flex flex-wrap gap-1.5">
            {detail.matched_skills.map(({ skill, proficiency_level }) => (
              <span
                key={skill.id}
                className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
              >
                {skill.name} · {proficiency_level}
              </span>
            ))}
          </div>
        </SectionCard>
      )}

      {detail.missing_skills.length > 0 && (
        <SectionCard title="Missing skills" description="Skills this posting lists that aren't on your profile yet.">
          <div className="flex flex-wrap gap-1.5">
            {detail.missing_skills.map((skill) => (
              <span
                key={skill.id}
                className="rounded-full bg-red-100 px-2 py-0.5 text-xs text-red-700 dark:bg-red-950 dark:text-red-400"
              >
                {skill.name}
              </span>
            ))}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
