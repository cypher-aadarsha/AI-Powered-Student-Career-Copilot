"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SectionCard } from "@/components/layout/section-card";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { careerApi } from "@/features/career/api";
import { ApiError } from "@/lib/api-client";
import type { CareerDetail } from "@/types/career";
import type { RoleLearningPlan } from "@/types/learning";

export default function CareerDetailPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const [detail, setDetail] = useState<CareerDetail | null>(null);
  const [learningPlan, setLearningPlan] = useState<RoleLearningPlan | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await careerApi.get(params.id);
        if (!cancelled) setDetail(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : "Could not load this role.");
      } finally {
        if (!cancelled) setIsLoading(false);
      }
      // Best-effort: the learning plan is a nice-to-have alongside the fit
      // score, so a failure here doesn't block the page from rendering.
      try {
        const plan = await careerApi.getLearningPlan(params.id);
        if (!cancelled) setLearningPlan(plan);
      } catch {
        // no-op — the "Close your skill gap" section just won't render
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
          {error ?? "Role not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <Link href="/careers" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
          ← All careers
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{detail.role.title}</h1>
        {detail.role.description && (
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{detail.role.description}</p>
        )}
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

      {detail.missing_required_skills.length > 0 && (
        <SectionCard title="Missing required skills" description="Focus here first — these count most toward your score.">
          <div className="flex flex-wrap gap-1.5">
            {detail.missing_required_skills.map((skill) => (
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

      {detail.missing_preferred_skills.length > 0 && (
        <SectionCard title="Missing preferred skills" description="Nice to have, worth less toward your score.">
          <div className="flex flex-wrap gap-1.5">
            {detail.missing_preferred_skills.map((skill) => (
              <span
                key={skill.id}
                className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
              >
                {skill.name}
              </span>
            ))}
          </div>
        </SectionCard>
      )}

      {learningPlan && (learningPlan.missing_required.length > 0 || learningPlan.missing_preferred.length > 0) && (
        <SectionCard title="Close your skill gap" description="Resources for each missing skill, most important first.">
          <div className="flex flex-col gap-4">
            {[...learningPlan.missing_required, ...learningPlan.missing_preferred].map(({ skill, resources }) => (
              <div key={skill.id}>
                <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{skill.name}</p>
                {resources.length === 0 ? (
                  <p className="mt-1 text-xs text-zinc-400">No resources yet for this skill.</p>
                ) : (
                  <ul className="mt-1 flex flex-col gap-1">
                    {resources.map((resource) => (
                      <li key={resource.id}>
                        <a
                          href={resource.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-sm text-zinc-500 underline hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-100"
                        >
                          {resource.title}
                        </a>
                        <span className="text-xs text-zinc-400"> · {resource.provider}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </SectionCard>
      )}
    </div>
  );
}
