"use client";

import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { ResumeCard } from "@/features/resume/resume-card";
import { UploadForm } from "@/features/resume/upload-form";
import { useResumes } from "@/features/resume/use-resumes";

export default function ResumePage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { resumes, isLoading, error, refetch } = useResumes();

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading your resumes…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Resume</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Resume &amp; AI analysis</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          Upload a PDF or DOCX resume for an explainable readability score, detected skills, and suggestions.
        </p>
      </div>

      <SectionCard title="Upload">
        <UploadForm onUploaded={refetch} />
      </SectionCard>

      <SectionCard title="Your resumes" description="Most recent first.">
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {resumes.length === 0 ? (
          <EmptyState label="No resumes uploaded yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {resumes.map((resume) => (
              <ResumeCard key={resume.id} resume={resume} onChange={refetch} />
            ))}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
