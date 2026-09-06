"use client";

import Link from "next/link";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { useJobs } from "@/features/job/use-jobs";

const employmentLabel: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  internship: "Internship",
  contract: "Contract",
};

export default function JobsPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { jobs, isLoading, error } = useJobs();

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading job matches…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Jobs</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Job matches</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Ranked by how well your current skills match each posting&apos;s requirements.
        </p>
      </div>

      <SectionCard title="Postings ranked by fit">
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {jobs.length === 0 ? (
          <EmptyState label="No job postings available yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {jobs.map((item) => (
              <li key={item.job.id}>
                <Link
                  href={`/jobs/${item.job.id}`}
                  className="block rounded-lg border border-zinc-100 p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{item.job.title}</h3>
                      <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">
                        {item.job.company} · {item.job.location}
                      </p>
                    </div>
                    <ScoreBar score={item.score} />
                  </div>
                  <p className="mt-2 text-xs text-zinc-400">
                    {employmentLabel[item.job.employment_type]}
                    {item.job.is_remote && " · Remote"} · {item.matched_skills}/{item.total_skills} skills matched
                  </p>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
