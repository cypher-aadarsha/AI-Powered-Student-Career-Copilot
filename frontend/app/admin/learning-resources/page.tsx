"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { useRequireAdmin } from "@/hooks/use-require-admin";
import { adminApi } from "@/features/admin/api";
import { SkillRefInput } from "@/features/admin/skill-ref-input";
import { ApiError } from "@/lib/api-client";
import type { AdminLearningResourceInput, AdminSkillRef } from "@/types/admin";
import type { LearningResource, ResourceType } from "@/types/learning";

const resourceTypes: { value: ResourceType; label: string }[] = [
  { value: "course", label: "Course" },
  { value: "tutorial", label: "Tutorial" },
  { value: "article", label: "Article" },
  { value: "video", label: "Video" },
  { value: "book", label: "Book" },
  { value: "documentation", label: "Documentation" },
];

const emptyForm: AdminLearningResourceInput = {
  title: "",
  description: "",
  url: "",
  provider: "",
  resource_type: "course",
  skills: [],
};

function toInput(resource: LearningResource): AdminLearningResourceInput {
  return {
    title: resource.title,
    description: resource.description,
    url: resource.url,
    provider: resource.provider,
    resource_type: resource.resource_type,
    skills: resource.skills.map((s) => ({ name: s.name, category: s.category })),
  };
}

function ResourceForm({
  initial,
  onCancel,
  onSaved,
}: {
  initial?: LearningResource;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<AdminLearningResourceInput>(initial ? toInput(initial) : emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = { ...form, description: form.description || null };
      if (initial) {
        await adminApi.updateLearningResource(initial.id, payload);
      } else {
        await adminApi.createLearningResource(payload);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save this resource. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Title</label>
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Provider</label>
          <input
            required
            value={form.provider}
            onChange={(e) => setForm({ ...form, provider: e.target.value })}
            placeholder="freeCodeCamp"
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">URL</label>
          <input
            required
            type="url"
            value={form.url}
            onChange={(e) => setForm({ ...form, url: e.target.value })}
            placeholder="https://example.com/guide"
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Type</label>
          <select
            value={form.resource_type}
            onChange={(e) => setForm({ ...form, resource_type: e.target.value as ResourceType })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          >
            {resourceTypes.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Description</label>
        <textarea
          value={form.description ?? ""}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
      </div>
      <SkillRefInput label="Skills taught" value={form.skills} onChange={(next: AdminSkillRef[]) => setForm({ ...form, skills: next })} />
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Create resource"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export default function AdminLearningResourcesPage() {
  const { isLoading: isAuthLoading, user } = useRequireAdmin();
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await adminApi.listLearningResources();
      setResources(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load learning resources.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [user, refetch]);

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
      </div>
    );
  }

  if (!user || user.role !== "admin") return null; // useRequireAdmin is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <Link href="/admin" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
          ← Admin panel
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Learning resources</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Shown in Learning and in career skill-gap plans.</p>
      </div>

      <SectionCard
        title={`${resources.length} resource${resources.length === 1 ? "" : "s"}`}
        action={
          !isAdding && (
            <Button variant="ghost" onClick={() => setIsAdding(true)}>
              + Add resource
            </Button>
          )
        }
      >
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {isAdding && (
          <ResourceForm
            onCancel={() => setIsAdding(false)}
            onSaved={() => {
              setIsAdding(false);
              refetch();
            }}
          />
        )}
        {resources.length === 0 && !isAdding ? (
          <EmptyState label="No learning resources yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {resources.map((resource) =>
              editingId === resource.id ? (
                <li key={resource.id}>
                  <ResourceForm
                    initial={resource}
                    onCancel={() => setEditingId(null)}
                    onSaved={() => {
                      setEditingId(null);
                      refetch();
                    }}
                  />
                </li>
              ) : (
                <li key={resource.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{resource.title}</h3>
                      <p className="mt-0.5 text-xs text-zinc-400">
                        {resource.provider} · {resource.resource_type}
                      </p>
                    </div>
                    <div className="flex shrink-0 gap-3">
                      <button
                        type="button"
                        onClick={() => setEditingId(resource.id)}
                        className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                      >
                        Edit
                      </button>
                      <InlineConfirmButton
                        onConfirm={async () => {
                          await adminApi.deleteLearningResource(resource.id);
                          refetch();
                        }}
                      />
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {resource.skills.map((s) => (
                      <span key={s.id} className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                        {s.name}
                      </span>
                    ))}
                  </div>
                </li>
              )
            )}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
