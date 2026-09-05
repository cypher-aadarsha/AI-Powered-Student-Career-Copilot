"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm, useWatch } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { SelectField } from "@/components/ui/select-field";
import { TextField } from "@/components/ui/text-field";
import { TextareaField } from "@/components/ui/textarea-field";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ApiError } from "@/lib/api-client";
import type { Experience } from "@/types/profile";
import { profileApi } from "./api";
import { employmentTypes, experienceSchema, type ExperienceInput, type ExperienceOutput } from "./schemas";

const employmentLabel: Record<string, string> = Object.fromEntries(employmentTypes.map((e) => [e.value, e.label]));

function ExperienceForm({
  initial,
  onCancel,
  onSaved,
}: {
  initial?: Experience;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm<ExperienceInput, unknown, ExperienceOutput>({
    resolver: zodResolver(experienceSchema),
    defaultValues: {
      title: initial?.title ?? "",
      company: initial?.company ?? "",
      employment_type: initial?.employment_type ?? "internship",
      start_date: initial?.start_date ?? "",
      end_date: initial?.end_date ?? "",
      is_current: initial?.is_current ?? false,
      description: initial?.description ?? "",
    },
  });
  const isCurrent = useWatch({ control, name: "is_current" });

  const onSubmit = async (input: ExperienceOutput) => {
    setServerError(null);
    try {
      if (initial) {
        await profileApi.updateExperience(initial.id, input);
      } else {
        await profileApi.addExperience(input);
      }
      onSaved();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Couldn't save this experience. Try again.");
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="mb-4 flex flex-col gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800"
      noValidate
    >
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <TextField label="Title" error={errors.title?.message} {...register("title")} />
        <TextField label="Company" error={errors.company?.message} {...register("company")} />
        <SelectField label="Type" options={employmentTypes} {...register("employment_type")} />
        <TextField label="Start date" type="date" error={errors.start_date?.message} {...register("start_date")} />
        {!isCurrent && (
          <TextField label="End date" type="date" error={errors.end_date?.message} {...register("end_date")} />
        )}
      </div>
      <label className="flex items-center gap-2 text-sm text-zinc-600 dark:text-zinc-300">
        <input type="checkbox" className="rounded" {...register("is_current")} />
        I currently work here
      </label>
      <TextareaField label="Description" error={errors.description?.message} {...register("description")} />

      {serverError && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {serverError}
        </p>
      )}

      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Add experience"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export function ExperiencesSection({ experiences, onChange }: { experiences: Experience[]; onChange: () => void }) {
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  return (
    <SectionCard
      title="Experience"
      description="Internships and jobs — what you did and where."
      action={
        !isAdding && (
          <Button variant="ghost" onClick={() => setIsAdding(true)}>
            + Add experience
          </Button>
        )
      }
    >
      {isAdding && (
        <ExperienceForm
          onCancel={() => setIsAdding(false)}
          onSaved={() => {
            setIsAdding(false);
            onChange();
          }}
        />
      )}

      {experiences.length === 0 && !isAdding ? (
        <EmptyState label="No experience added yet." />
      ) : (
        <ul className="flex flex-col gap-3">
          {experiences.map((experience) =>
            editingId === experience.id ? (
              <li key={experience.id}>
                <ExperienceForm
                  initial={experience}
                  onCancel={() => setEditingId(null)}
                  onSaved={() => {
                    setEditingId(null);
                    onChange();
                  }}
                />
              </li>
            ) : (
              <li key={experience.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-medium text-zinc-900 dark:text-zinc-50">
                      {experience.title} · {experience.company}
                    </h3>
                    <p className="text-xs text-zinc-400">
                      {employmentLabel[experience.employment_type]} · {experience.start_date} –{" "}
                      {experience.is_current ? "present" : experience.end_date ?? "—"}
                    </p>
                  </div>
                  <div className="flex shrink-0 gap-3">
                    <button
                      type="button"
                      onClick={() => setEditingId(experience.id)}
                      className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                    >
                      Edit
                    </button>
                    <InlineConfirmButton
                      onConfirm={async () => {
                        await profileApi.deleteExperience(experience.id);
                        onChange();
                      }}
                    />
                  </div>
                </div>
                {experience.description && (
                  <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{experience.description}</p>
                )}
              </li>
            )
          )}
        </ul>
      )}
    </SectionCard>
  );
}
