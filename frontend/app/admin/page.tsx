"use client";

import Link from "next/link";
import { BookOpen, Briefcase, GraduationCap, MessageSquare, Users } from "lucide-react";

import { useRequireAdmin } from "@/hooks/use-require-admin";

const sections = [
  {
    href: "/admin/users",
    icon: Users,
    title: "Users",
    description: "View student and admin accounts; activate or deactivate.",
  },
  {
    href: "/admin/career-roles",
    icon: GraduationCap,
    title: "Career roles",
    description: "The curated catalogue students match against in Careers.",
  },
  {
    href: "/admin/learning-resources",
    icon: BookOpen,
    title: "Learning resources",
    description: "Courses, docs, and tutorials shown in Learning and skill-gap plans.",
  },
  {
    href: "/admin/job-postings",
    icon: Briefcase,
    title: "Job postings",
    description: "Demo postings students match against in Jobs.",
  },
  {
    href: "/admin/interview-questions",
    icon: MessageSquare,
    title: "Interview questions",
    description: "The question bank mock interview sessions draw from.",
  },
];

export default function AdminPage() {
  const { isLoading, user } = useRequireAdmin();

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
      </div>
    );
  }

  if (!user || user.role !== "admin") return null; // useRequireAdmin is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Admin</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Admin panel</h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Manage the platform-curated catalogues every student-facing module reads from.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="flex items-start gap-4 rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
              <section.icon size={18} strokeWidth={2} />
            </div>
            <div>
              <h2 className="font-medium text-zinc-900 dark:text-zinc-50">{section.title}</h2>
              <p className="mt-0.5 text-sm text-zinc-500 dark:text-zinc-400">{section.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
