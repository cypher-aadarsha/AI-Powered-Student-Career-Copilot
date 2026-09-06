"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { SectionCard } from "@/components/layout/section-card";
import { useRequireAdmin } from "@/hooks/use-require-admin";
import { adminApi } from "@/features/admin/api";
import { ApiError } from "@/lib/api-client";
import type { AdminUser } from "@/types/admin";

function UserRow({ target, currentUserId, onChange }: { target: AdminUser; currentUserId: string; onChange: () => void }) {
  const [isSaving, setIsSaving] = useState(false);
  const isSelf = target.id === currentUserId;

  const toggle = async () => {
    setIsSaving(true);
    try {
      await adminApi.setUserActive(target.id, !target.is_active);
      onChange();
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <li className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
      <div>
        <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
          {target.full_name} {isSelf && <span className="text-xs text-zinc-400">(you)</span>}
        </p>
        <p className="text-xs text-zinc-400">
          {target.email} · {target.role} · joined {new Date(target.created_at).toLocaleDateString()}
        </p>
      </div>
      <div className="flex items-center gap-3">
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
            target.is_active
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
              : "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
          }`}
        >
          {target.is_active ? "Active" : "Deactivated"}
        </span>
        <button
          type="button"
          disabled={isSaving || (isSelf && target.is_active)}
          onClick={toggle}
          title={isSelf && target.is_active ? "You can't deactivate your own account" : undefined}
          className="text-xs font-medium text-zinc-500 hover:text-zinc-900 disabled:cursor-not-allowed disabled:opacity-40 dark:text-zinc-400 dark:hover:text-zinc-50"
        >
          {isSaving ? "Saving…" : target.is_active ? "Deactivate" : "Activate"}
        </button>
      </div>
    </li>
  );
}

export default function AdminUsersPage() {
  const { isLoading: isAuthLoading, user } = useRequireAdmin();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await adminApi.listUsers();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load users.");
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
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Users</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Deactivating an account blocks login immediately without deleting any of their data.
        </p>
      </div>

      <SectionCard title={`${users.length} account${users.length === 1 ? "" : "s"}`}>
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        <ul className="flex flex-col gap-3">
          {users.map((target) => (
            <UserRow key={target.id} target={target} currentUserId={user.id} onChange={refetch} />
          ))}
        </ul>
      </SectionCard>
    </div>
  );
}
