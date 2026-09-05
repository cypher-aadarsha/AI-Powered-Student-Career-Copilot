import { ApiError, apiFetch } from "@/lib/api-client";
import type { HealthStatus } from "@/types/health";

// This route is a Phase 2 scaffolding check, not the product landing page
// (that lands with the marketing/onboarding phase). It proves the frontend
// container can reach the backend container, and the backend can reach
// Postgres, from one page load.
export const dynamic = "force-dynamic";

async function getHealth(): Promise<{ status: HealthStatus | null; error: string | null }> {
  try {
    const status = await apiFetch<HealthStatus>("/api/v1/health");
    return { status, error: null };
  } catch (err) {
    const message = err instanceof ApiError ? err.message : "Could not reach the API.";
    return { status: null, error: message };
  }
}

function Pill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-medium ${
        ok ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400"
           : "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-400"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-emerald-500" : "bg-red-500"}`} />
      {label}
    </span>
  );
}

export default async function Home() {
  const { status, error } = await getHealth();

  return (
    <div className="flex flex-1 items-center justify-center bg-zinc-50 px-6 dark:bg-black">
      <main className="w-full max-w-lg rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Career Copilot &middot; Phase 2</p>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Project scaffold status</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          This page will become the product landing page in a later phase. For now it confirms the stack boots
          end-to-end: frontend &rarr; API &rarr; database.
        </p>

        <dl className="mt-6 flex flex-col gap-3">
          <div className="flex items-center justify-between rounded-lg border border-zinc-100 px-4 py-3 dark:border-zinc-800">
            <dt className="text-sm text-zinc-600 dark:text-zinc-300">API</dt>
            <dd><Pill ok={Boolean(status)} label={status ? "reachable" : "unreachable"} /></dd>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-zinc-100 px-4 py-3 dark:border-zinc-800">
            <dt className="text-sm text-zinc-600 dark:text-zinc-300">Database</dt>
            <dd>
              <Pill
                ok={status?.database === "connected"}
                label={status?.database ?? "unknown"}
              />
            </dd>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-zinc-100 px-4 py-3 dark:border-zinc-800">
            <dt className="text-sm text-zinc-600 dark:text-zinc-300">Environment</dt>
            <dd className="text-sm font-mono text-zinc-700 dark:text-zinc-300">{status?.environment ?? "—"}</dd>
          </div>
        </dl>

        {error && (
          <p className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
            {error} Start the backend (see README) and reload.
          </p>
        )}

        <p className="mt-6 text-xs text-zinc-400">
          API docs: <a className="underline" href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/docs`}>/docs</a>
        </p>
      </main>
    </div>
  );
}
