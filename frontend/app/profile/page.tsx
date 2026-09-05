"use client";

import { SectionCard } from "@/components/layout/section-card";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { CertificationsSection } from "@/features/profile/certifications-section";
import { ExperiencesSection } from "@/features/profile/experiences-section";
import { ProfileForm } from "@/features/profile/profile-form";
import { ProjectsSection } from "@/features/profile/projects-section";
import { SkillsSection } from "@/features/profile/skills-section";
import { useProfile } from "@/features/profile/use-profile";

export default function ProfilePage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const { profile, isLoading: isProfileLoading, error, refetch } = useProfile();

  if (isAuthLoading || (user && isProfileLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading your profile…</p>
      </div>
    );
  }

  if (!user) return null; // useRequireAuth is already redirecting

  if (error || !profile) {
    return (
      <div className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-sm rounded-lg bg-red-50 px-4 py-3 text-center text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
          {error ?? "Something went wrong loading your profile."}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <p className="text-xs font-semibold tracking-wide text-zinc-400 uppercase">Profile</p>
        <h1 className="mt-1 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{user.full_name}</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">{user.email}</p>
      </div>

      <SectionCard title="About you">
        <ProfileForm profile={profile} onSaved={refetch} />
      </SectionCard>

      <SkillsSection skills={profile.skills} onChange={refetch} />
      <ProjectsSection projects={profile.projects} availableSkills={profile.skills} onChange={refetch} />
      <ExperiencesSection experiences={profile.experiences} onChange={refetch} />
      <CertificationsSection certifications={profile.certifications} onChange={refetch} />
    </div>
  );
}
