"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { TextareaField } from "@/components/ui/textarea-field";
import { ApiError } from "@/lib/api-client";
import type { StudentProfile } from "@/types/profile";
import { profileApi } from "./api";
import { profileUpdateSchema, type ProfileUpdateInput, type ProfileUpdateOutput } from "./schemas";

export function ProfileForm({ profile, onSaved }: { profile: StudentProfile; onSaved: () => void }) {
  const [serverError, setServerError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileUpdateInput, unknown, ProfileUpdateOutput>({
    resolver: zodResolver(profileUpdateSchema),
    defaultValues: {
      university: profile.university ?? "",
      degree: profile.degree ?? "",
      semester: profile.semester ?? "",
      graduation_year: profile.graduation_year ?? "",
      location: profile.location ?? "",
      bio: profile.bio ?? "",
      github_url: profile.github_url ?? "",
      linkedin_url: profile.linkedin_url ?? "",
      portfolio_url: profile.portfolio_url ?? "",
    },
  });

  const onSubmit = async (input: ProfileUpdateOutput) => {
    setServerError(null);
    setSaved(false);
    try {
      await profileApi.update(input);
      setSaved(true);
      onSaved();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Couldn't save your profile. Try again.");
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <TextField label="University / College" error={errors.university?.message} {...register("university")} />
        <TextField label="Degree" placeholder="BSc. CSIT" error={errors.degree?.message} {...register("degree")} />
        <TextField
          label="Semester"
          type="number"
          min={1}
          max={12}
          error={errors.semester?.message}
          {...register("semester")}
        />
        <TextField
          label="Graduation year"
          type="number"
          min={2000}
          max={2100}
          error={errors.graduation_year?.message}
          {...register("graduation_year")}
        />
        <TextField
          label="Location"
          placeholder="Kathmandu, Nepal"
          error={errors.location?.message}
          {...register("location")}
        />
      </div>

      <TextareaField
        label="Bio"
        placeholder="A short summary of who you are and what you're working toward."
        error={errors.bio?.message}
        {...register("bio")}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <TextField
          label="GitHub"
          placeholder="https://github.com/you"
          error={errors.github_url?.message}
          {...register("github_url")}
        />
        <TextField
          label="LinkedIn"
          placeholder="https://linkedin.com/in/you"
          error={errors.linkedin_url?.message}
          {...register("linkedin_url")}
        />
        <TextField
          label="Portfolio"
          placeholder="https://you.dev"
          error={errors.portfolio_url?.message}
          {...register("portfolio_url")}
        />
      </div>

      {serverError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
          {serverError}
        </p>
      )}

      <div className="flex items-center gap-3">
        <Button type="submit" isLoading={isSubmitting} className="self-start">
          Save profile
        </Button>
        {saved && !isSubmitting && <span className="text-sm text-emerald-600 dark:text-emerald-400">Saved.</span>}
      </div>
    </form>
  );
}
