"use client";

import Link from "next/link";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { useCareers } from "@/features/career/use-careers";

export default function CareersPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { careers, isLoading, error } = useCareers();

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading career matches…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Careers</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Career fit &amp; skill gaps</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Ranked by how well your current skills match each role. Add skills on your profile to improve your fit.
        </p>
      </div>

      <SectionCard title="Roles ranked by fit">
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {careers.length === 0 ? (
          <EmptyState label="No career roles available yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {careers.map((item) => (
              <li key={item.role.id}>
                <Link
                  href={`/careers/${item.role.id}`}
                  className="block rounded-lg border border-zinc-100 p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{item.role.title}</h3>
                      {item.role.description && (
                        <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">{item.role.description}</p>
                      )}
                    </div>
                    <ScoreBar score={item.score} />
                  </div>
                  <p className="mt-2 text-xs text-zinc-400">
                    {item.matched_required}/{item.total_required} required skills
                    {item.total_preferred > 0 && ` · ${item.matched_preferred}/${item.total_preferred} preferred`}
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
