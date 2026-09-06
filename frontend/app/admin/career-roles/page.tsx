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
import type { AdminCareerRole, AdminCareerRoleInput, AdminSkillRef } from "@/types/admin";

const emptyForm: AdminCareerRoleInput = { title: "", description: "", required_skills: [], preferred_skills: [] };

function toInput(role: AdminCareerRole): AdminCareerRoleInput {
  return {
    title: role.title,
    description: role.description,
    required_skills: role.required_skills.map((s) => ({ name: s.name, category: s.category })),
    preferred_skills: role.preferred_skills.map((s) => ({ name: s.name, category: s.category })),
  };
}

function RoleForm({
  initial,
  onCancel,
  onSaved,
}: {
  initial?: AdminCareerRole;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<AdminCareerRoleInput>(initial ? toInput(initial) : emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = { ...form, description: form.description || null };
      if (initial) {
        await adminApi.updateCareerRole(initial.id, payload);
      } else {
        await adminApi.createCareerRole(payload);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save this role. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
      <div>
        <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Title</label>
        <input
          required
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          placeholder="Backend Developer"
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
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
      <SkillRefInput
        label="Required skills"
        value={form.required_skills}
        onChange={(next: AdminSkillRef[]) => setForm({ ...form, required_skills: next })}
      />
      <SkillRefInput
        label="Preferred skills"
        value={form.preferred_skills}
        onChange={(next: AdminSkillRef[]) => setForm({ ...form, preferred_skills: next })}
      />
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Create role"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export default function AdminCareerRolesPage() {
  const { isLoading: isAuthLoading, user } = useRequireAdmin();
  const [roles, setRoles] = useState<AdminCareerRole[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await adminApi.listCareerRoles();
      setRoles(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load career roles.");
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
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Career roles</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">The catalogue students match against in Careers.</p>
      </div>

      <SectionCard
        title={`${roles.length} role${roles.length === 1 ? "" : "s"}`}
        action={
          !isAdding && (
            <Button variant="ghost" onClick={() => setIsAdding(true)}>
              + Add role
            </Button>
          )
        }
      >
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {isAdding && (
          <RoleForm
            onCancel={() => setIsAdding(false)}
            onSaved={() => {
              setIsAdding(false);
              refetch();
            }}
          />
        )}
        {roles.length === 0 && !isAdding ? (
          <EmptyState label="No career roles yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {roles.map((role) =>
              editingId === role.id ? (
                <li key={role.id}>
                  <RoleForm
                    initial={role}
                    onCancel={() => setEditingId(null)}
                    onSaved={() => {
                      setEditingId(null);
                      refetch();
                    }}
                  />
                </li>
              ) : (
                <li key={role.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{role.title}</h3>
                      {role.description && <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">{role.description}</p>}
                    </div>
                    <div className="flex shrink-0 gap-3">
                      <button
                        type="button"
                        onClick={() => setEditingId(role.id)}
                        className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                      >
                        Edit
                      </button>
                      <InlineConfirmButton
                        onConfirm={async () => {
                          await adminApi.deleteCareerRole(role.id);
                          refetch();
                        }}
                      />
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {role.required_skills.map((s) => (
                      <span key={s.id} className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                        {s.name}
                      </span>
                    ))}
                    {role.preferred_skills.map((s) => (
                      <span key={s.id} className="rounded-full border border-dashed border-zinc-200 px-2 py-0.5 text-xs text-zinc-400 dark:border-zinc-700">
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
