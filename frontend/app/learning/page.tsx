"use client";

import { useMemo, useState } from "react";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { useLearningResources } from "@/features/learning/use-learning-resources";

const resourceTypeLabel: Record<string, string> = {
  course: "Course",
  tutorial: "Tutorial",
  article: "Article",
  video: "Video",
  book: "Book",
  documentation: "Documentation",
};

export default function LearningPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const [skillFilter, setSkillFilter] = useState<{ id: string; name: string } | null>(null);
  const { resources, isLoading, error } = useLearningResources(skillFilter?.id);
  // Separate, always-unfiltered fetch used only to build the filter chip
  // list — kept independent of the (possibly filtered) display list above
  // instead of a dedicated "list all skills" endpoint, since the catalogue
  // is small. Plain derived state via useMemo, no ref/effect needed.
  const { resources: allResources } = useLearningResources();

  const skillOptions = useMemo(() => {
    const bySkillId = new Map<string, string>();
    for (const resource of allResources) {
      for (const skill of resource.skills) bySkillId.set(skill.id, skill.name);
    }
    return Array.from(bySkillId, ([id, name]) => ({ id, name })).sort((a, b) => a.name.localeCompare(b.name));
  }, [allResources]);

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading learning resources…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Learning</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Learning resources</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Curated courses, docs, and tutorials. Missing skills on a career&apos;s page link back here.
        </p>
      </div>

      {skillOptions.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => setSkillFilter(null)}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              skillFilter === null
                ? "bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-900"
                : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
            }`}
          >
            All
          </button>
          {skillOptions.map((skill) => (
            <button
              key={skill.id}
              type="button"
              onClick={() => setSkillFilter(skill)}
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                skillFilter?.id === skill.id
                  ? "bg-zinc-900 text-zinc-50 dark:bg-zinc-50 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
              }`}
            >
              {skill.name}
            </button>
          ))}
        </div>
      )}

      <SectionCard title={skillFilter ? `Resources for ${skillFilter.name}` : "All resources"}>
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {resources.length === 0 ? (
          <EmptyState label="No learning resources found." />
        ) : (
          <ul className="flex flex-col gap-3">
            {resources.map((resource) => (
              <li key={resource.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{resource.title}</h3>
                    <p className="mt-0.5 text-xs text-zinc-400">
                      {resource.provider} · {resourceTypeLabel[resource.resource_type]}
                    </p>
                  </div>
                  <a
                    href={resource.url}
                    target="_blank"
                    rel="noreferrer"
                    className="shrink-0 text-xs font-medium text-zinc-500 hover:text-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-100"
                  >
                    Open resource ↗
                  </a>
                </div>
                {resource.description && (
                  <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300">{resource.description}</p>
                )}
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {resource.skills.map((skill) => (
                    <span
                      key={skill.id}
                      className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                    >
                      {skill.name}
                    </span>
                  ))}
                </div>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
