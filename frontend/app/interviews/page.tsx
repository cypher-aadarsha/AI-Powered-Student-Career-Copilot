"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { Button } from "@/components/ui/button";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { interviewApi } from "@/features/interview/api";
import { useInterviewSessions } from "@/features/interview/use-interview-sessions";
import { useCareers } from "@/features/career/use-careers";
import { ApiError } from "@/lib/api-client";

const statusLabel: Record<string, string> = {
  in_progress: "In progress",
  completed: "Completed",
};

const statusColor: Record<string, string> = {
  in_progress: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400",
  completed: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-400",
};

function StartSessionForm() {
  const router = useRouter();
  const { careers } = useCareers();
  const [roleId, setRoleId] = useState<string>("");
  const [questionCount, setQuestionCount] = useState(5);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    setIsStarting(true);
    setError(null);
    try {
      const session = await interviewApi.startSession({
        career_role_id: roleId || undefined,
        question_count: questionCount,
      });
      router.push(`/interviews/${session.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't start a mock interview. Try again.");
      setIsStarting(false);
    }
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm text-zinc-600 dark:text-zinc-300">Practice for a role (optional)</label>
          <select
            value={roleId}
            onChange={(e) => setRoleId(e.target.value)}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          >
            <option value="">General mix</option>
            {careers.map((item) => (
              <option key={item.role.id} value={item.role.id}>
                {item.role.title}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm text-zinc-600 dark:text-zinc-300">Number of questions</label>
          <select
            value={questionCount}
            onChange={(e) => setQuestionCount(Number(e.target.value))}
            className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
          >
            {[3, 5, 7, 10].map((count) => (
              <option key={count} value={count}>
                {count}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-end">
          <Button type="button" onClick={handleStart} isLoading={isStarting} className="w-full">
            Start mock interview
          </Button>
        </div>
      </div>
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}

export default function InterviewsPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { sessions, isLoading, error } = useInterviewSessions();

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading your mock interviews…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Interview prep</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Mock interviews</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Practice behavioral, situational, and technical questions with instant AI feedback.
        </p>
      </div>

      <SectionCard title="Start a new mock interview">
        <StartSessionForm />
      </SectionCard>

      <SectionCard title="Your sessions">
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {sessions.length === 0 ? (
          <EmptyState label="No mock interviews yet — start one above." />
        ) : (
          <ul className="flex flex-col gap-3">
            {sessions.map((session) => (
              <li key={session.id}>
                <Link
                  href={`/interviews/${session.id}`}
                  className="block rounded-lg border border-zinc-100 p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-medium text-zinc-900 dark:text-zinc-50">
                        {session.career_role ? session.career_role.title : "General mock interview"}
                      </h3>
                      <p className="mt-0.5 text-xs text-zinc-400">
                        {session.answered_count}/{session.question_count} answered ·{" "}
                        {new Date(session.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColor[session.status]}`}>
                        {statusLabel[session.status]}
                      </span>
                      {session.average_score !== null && <ScoreBar score={session.average_score} />}
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
