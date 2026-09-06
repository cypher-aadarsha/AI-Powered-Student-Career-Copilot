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
import type { AdminJobPosting, AdminJobPostingInput, AdminSkillRef } from "@/types/admin";
import type { JobEmploymentType } from "@/types/job";

const employmentTypes: { value: JobEmploymentType; label: string }[] = [
  { value: "full_time", label: "Full-time" },
  { value: "part_time", label: "Part-time" },
  { value: "internship", label: "Internship" },
  { value: "contract", label: "Contract" },
];

const emptyForm: AdminJobPostingInput = {
  title: "",
  company: "",
  location: "",
  employment_type: "full_time",
  is_remote: false,
  description: "",
  apply_url: "",
  skills: [],
};

function toInput(job: AdminJobPosting): AdminJobPostingInput {
  return {
    title: job.title,
    company: job.company,
    location: job.location,
    employment_type: job.employment_type,
    is_remote: job.is_remote,
    description: job.description,
    apply_url: job.apply_url,
    skills: job.skills.map((s) => ({ name: s.name, category: s.category })),
  };
}

function JobForm({ initial, onCancel, onSaved }: { initial?: AdminJobPosting; onCancel: () => void; onSaved: () => void }) {
  const [form, setForm] = useState<AdminJobPostingInput>(initial ? toInput(initial) : emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = { ...form, description: form.description || null };
      if (initial) {
        await adminApi.updateJobPosting(initial.id, payload);
      } else {
        await adminApi.createJobPosting(payload);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save this posting. Try again.");
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
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Company</label>
          <input
            required
            value={form.company}
            onChange={(e) => setForm({ ...form, company: e.target.value })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Location</label>
          <input
            required
            value={form.location}
            onChange={(e) => setForm({ ...form, location: e.target.value })}
            placeholder="Kathmandu, Nepal"
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Employment type</label>
          <select
            value={form.employment_type}
            onChange={(e) => setForm({ ...form, employment_type: e.target.value as JobEmploymentType })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          >
            {employmentTypes.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Apply URL</label>
          <input
            required
            type="url"
            value={form.apply_url}
            onChange={(e) => setForm({ ...form, apply_url: e.target.value })}
            placeholder="https://example.com/careers/role"
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          />
        </div>
      </div>
      <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300">
        <input type="checkbox" checked={form.is_remote} onChange={(e) => setForm({ ...form, is_remote: e.target.checked })} className="rounded" />
        Remote
      </label>
      <div>
        <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Description</label>
        <textarea
          value={form.description ?? ""}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
      </div>
      <SkillRefInput label="Required skills" value={form.skills} onChange={(next: AdminSkillRef[]) => setForm({ ...form, skills: next })} />
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Create posting"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export default function AdminJobPostingsPage() {
  const { isLoading: isAuthLoading, user } = useRequireAdmin();
  const [jobs, setJobs] = useState<AdminJobPosting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await adminApi.listJobPostings();
      setJobs(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load job postings.");
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
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Job postings</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Demo postings students match against in Jobs.</p>
      </div>

      <SectionCard
        title={`${jobs.length} posting${jobs.length === 1 ? "" : "s"}`}
        action={
          !isAdding && (
            <Button variant="ghost" onClick={() => setIsAdding(true)}>
              + Add posting
            </Button>
          )
        }
      >
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {isAdding && (
          <JobForm
            onCancel={() => setIsAdding(false)}
            onSaved={() => {
              setIsAdding(false);
              refetch();
            }}
          />
        )}
        {jobs.length === 0 && !isAdding ? (
          <EmptyState label="No job postings yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {jobs.map((job) =>
              editingId === job.id ? (
                <li key={job.id}>
                  <JobForm
                    initial={job}
                    onCancel={() => setEditingId(null)}
                    onSaved={() => {
                      setEditingId(null);
                      refetch();
                    }}
                  />
                </li>
              ) : (
                <li key={job.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{job.title}</h3>
                      <p className="mt-0.5 text-xs text-zinc-400">
                        {job.company} · {job.location} · {job.employment_type}
                        {job.is_remote && " · Remote"}
                      </p>
                    </div>
                    <div className="flex shrink-0 gap-3">
                      <button
                        type="button"
                        onClick={() => setEditingId(job.id)}
                        className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                      >
                        Edit
                      </button>
                      <InlineConfirmButton
                        onConfirm={async () => {
                          await adminApi.deleteJobPosting(job.id);
                          refetch();
                        }}
                      />
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {job.skills.map((s) => (
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
