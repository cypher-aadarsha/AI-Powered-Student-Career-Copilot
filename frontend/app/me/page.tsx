"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-context";
import { useRequireAuth } from "@/hooks/use-require-auth";

// Stand-in protected page for Phase 3 (proves the auth + route-guard wiring
// end-to-end). The real dashboard — readiness score, skill gaps,
// recommendations — replaces this in Phase 9.
export default function MePage() {
  const { user, isLoading } = useRequireAuth();
  const { logout } = useAuth();
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading your account…</p>
      </div>
    );
  }

  if (!user) {
    // useRequireAuth is already redirecting; render nothing in the meantime.
    return null;
  }

  return (
    <div className="flex flex-1 items-center justify-center bg-zinc-50 px-6 dark:bg-black">
      <main className="w-full max-w-lg rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Protected route</p>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Welcome, {user.full_name}
        </h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          This page only renders for a signed-in user — the real dashboard (readiness score, skill
          gaps, recommendations) arrives in a later phase.
        </p>

        <dl className="mt-6 flex flex-col gap-3">
          <Row label="Email" value={user.email} />
          <Row label="Role" value={user.role} />
          <Row label="Account created" value={new Date(user.created_at).toLocaleDateString()} />
        </dl>

        <Button
          variant="ghost"
          className="mt-6"
          onClick={async () => {
            await logout();
            router.push("/login");
          }}
        >
          Log out
        </Button>
      </main>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-zinc-100 px-4 py-3 dark:border-zinc-800">
      <dt className="text-sm text-zinc-600 dark:text-zinc-300">{label}</dt>
      <dd className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{value}</dd>
    </div>
  );
}
