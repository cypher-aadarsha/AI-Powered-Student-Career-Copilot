"use client";

import Link from "next/link";
import { ArrowRight, Briefcase, CheckCircle2, Circle, FileText, GraduationCap, MessageSquare, Sparkles, Target } from "lucide-react";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ProgressRing } from "@/components/ui/progress-ring";
import { ScoreBar } from "@/components/ui/score-bar";
import { StatCard } from "@/components/ui/stat-card";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { useDashboard } from "@/features/dashboard/use-dashboard";

/** Best-effort routing for a suggestion string — every suggestion the
 * backend generates names one clear next action, so a substring match is
 * enough to send the student to the right page. */
function suggestionHref(suggestion: string): string {
  const lower = suggestion.toLowerCase();
  if (lower.includes("resume")) return "/resume";
  if (lower.includes("mock interview")) return "/interviews";
  if (lower.includes("career match")) return "/careers";
  return "/profile";
}

export default function DashboardPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { dashboard, isLoading, error } = useDashboard();

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading your dashboard…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  if (error || !dashboard) {
    return (
      <div className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-sm rounded-lg bg-red-50 px-4 py-3 text-center text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
          {error ?? "Something went wrong loading your dashboard."}
        </div>
      </div>
    );
  }

  const bestCareerScore = dashboard.top_career_matches[0]?.score ?? null;
  const resumeScoreLabel = dashboard.latest_resume?.ai_score != null ? `${dashboard.latest_resume.ai_score}/100` : "—";
  const resumeHint = !dashboard.latest_resume
    ? "Not uploaded yet"
    : dashboard.latest_resume.ai_score == null
      ? `Status: ${dashboard.latest_resume.status}`
      : undefined;

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-10">
      {/* Hero */}
      <div className="flex flex-col items-start justify-between gap-6 rounded-2xl border border-zinc-200 bg-gradient-to-br from-indigo-50 via-white to-white p-6 shadow-sm sm:flex-row sm:items-center dark:border-zinc-800 dark:from-indigo-950/20 dark:via-zinc-950 dark:to-zinc-950">
        <div>
          <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Dashboard</p>
          <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
            Welcome back, {user.full_name.split(" ")[0]}
          </h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
            Here&apos;s where your career readiness stands today.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link
              href="/profile"
              className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-medium text-zinc-50 hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              Edit profile
            </Link>
            <Link
              href="/interviews"
              className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm font-medium text-zinc-600 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
            >
              Practice interview
            </Link>
          </div>
        </div>
        <div className="flex flex-col items-center gap-1">
          <ProgressRing score={dashboard.profile_completion.score} size={104} label="complete" />
          <span className="text-xs text-zinc-400">Profile strength</span>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard icon={Sparkles} label="Skills" value={String(dashboard.skill_count)} />
        <StatCard icon={FileText} label="Resume score" value={resumeScoreLabel} hint={resumeHint} />
        <StatCard
          icon={Target}
          label="Best career match"
          value={bestCareerScore !== null ? `${bestCareerScore}%` : "—"}
        />
        <StatCard
          icon={MessageSquare}
          label="Interview avg."
          value={dashboard.interview_stats.average_score !== null ? `${dashboard.interview_stats.average_score}/100` : "—"}
          hint={`${dashboard.interview_stats.total_sessions} session${dashboard.interview_stats.total_sessions === 1 ? "" : "s"}`}
        />
      </div>

      {/* Checklist + suggestions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <SectionCard title="Complete your profile" description={`${dashboard.profile_completion.score}% complete`}>
          <ul className="flex flex-col gap-2">
            {dashboard.profile_completion.checklist.map((item) => (
              <li key={item.label} className="flex items-center gap-2 text-sm">
                {item.done ? (
                  <CheckCircle2 size={16} className="shrink-0 text-emerald-500" />
                ) : (
                  <Circle size={16} className="shrink-0 text-zinc-300 dark:text-zinc-700" />
                )}
                <span
                  className={
                    item.done
                      ? "text-zinc-500 line-through dark:text-zinc-500"
                      : "text-zinc-700 dark:text-zinc-200"
                  }
                >
                  {item.label}
                </span>
              </li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard title="Suggested next steps">
          {dashboard.suggested_actions.length === 0 ? (
            <EmptyState label="You're all caught up — nice work." />
          ) : (
            <ul className="flex flex-col gap-2">
              {dashboard.suggested_actions.map((suggestion) => (
                <li key={suggestion}>
                  <Link
                    href={suggestionHref(suggestion)}
                    className="flex items-center justify-between gap-3 rounded-lg border border-zinc-100 px-3 py-2 text-sm text-zinc-600 transition-colors hover:border-zinc-300 hover:text-zinc-900 dark:border-zinc-800 dark:text-zinc-300 dark:hover:border-zinc-700 dark:hover:text-zinc-50"
                  >
                    <span>{suggestion}</span>
                    <ArrowRight size={14} className="shrink-0" />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </SectionCard>
      </div>

      {/* Top career matches */}
      <SectionCard
        title="Top career matches"
        description="Ranked by your current skills."
        action={
          <Link href="/careers" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
            View all
          </Link>
        }
      >
        {dashboard.top_career_matches.length === 0 ? (
          <EmptyState label="No career roles available yet." />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {dashboard.top_career_matches.map((item) => (
              <Link
                key={item.role.id}
                href={`/careers/${item.role.id}`}
                className="flex flex-col gap-2 rounded-lg border border-zinc-100 p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
              >
                <div className="flex items-center gap-2">
                  <GraduationCap size={16} className="shrink-0 text-zinc-400" />
                  <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{item.role.title}</h3>
                </div>
                <ScoreBar score={item.score} />
              </Link>
            ))}
          </div>
        )}
      </SectionCard>

      {/* Top job matches */}
      <SectionCard
        title="Top job matches"
        description="Demo postings ranked by fit."
        action={
          <Link href="/jobs" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
            View all
          </Link>
        }
      >
        {dashboard.top_job_matches.length === 0 ? (
          <EmptyState label="No job postings available yet." />
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {dashboard.top_job_matches.map((item) => (
              <Link
                key={item.job.id}
                href={`/jobs/${item.job.id}`}
                className="flex flex-col gap-2 rounded-lg border border-zinc-100 p-4 transition-colors hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
              >
                <div className="flex items-center gap-2">
                  <Briefcase size={16} className="shrink-0 text-zinc-400" />
                  <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{item.job.title}</h3>
                </div>
                <p className="text-xs text-zinc-400">{item.job.company}</p>
                <ScoreBar score={item.score} />
              </Link>
            ))}
          </div>
        )}
      </SectionCard>
    </div>
  );
}
