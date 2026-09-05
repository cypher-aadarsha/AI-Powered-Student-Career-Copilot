"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { SelectField } from "@/components/ui/select-field";
import { TextField } from "@/components/ui/text-field";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ApiError } from "@/lib/api-client";
import type { StudentSkill } from "@/types/profile";
import { profileApi } from "./api";
import { proficiencyLevels, skillCategories, skillSchema, type SkillInput } from "./schemas";

const proficiencyLabel: Record<string, string> = Object.fromEntries(
  proficiencyLevels.map((p) => [p.value, p.label])
);

export function SkillsSection({ skills, onChange }: { skills: StudentSkill[]; onChange: () => void }) {
  const [isAdding, setIsAdding] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SkillInput>({
    resolver: zodResolver(skillSchema),
    defaultValues: { name: "", category: "technical", proficiency_level: "beginner" },
  });

  const onSubmit = async (input: SkillInput) => {
    setServerError(null);
    try {
      await profileApi.addSkill(input);
      reset();
      setIsAdding(false);
      onChange();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Couldn't add that skill. Try again.");
    }
  };

  return (
    <SectionCard
      title="Skills"
      description="Technical skills, programming languages, frameworks, tools, and soft skills."
      action={
        !isAdding && (
          <Button variant="ghost" onClick={() => setIsAdding(true)}>
            + Add skill
          </Button>
        )
      }
    >
      {isAdding && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="mb-4 grid grid-cols-1 gap-3 rounded-lg border border-zinc-100 p-4 sm:grid-cols-4 dark:border-zinc-800"
          noValidate
        >
          <div className="sm:col-span-2">
            <TextField label="Skill" placeholder="React" error={errors.name?.message} {...register("name")} />
          </div>
          <SelectField label="Category" options={skillCategories} {...register("category")} />
          <SelectField label="Proficiency" options={proficiencyLevels} {...register("proficiency_level")} />
          {serverError && (
            <p role="alert" className="sm:col-span-4 text-sm text-red-600 dark:text-red-400">
              {serverError}
            </p>
          )}
          <div className="flex gap-2 sm:col-span-4">
            <Button type="submit" isLoading={isSubmitting}>
              Add
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => {
                reset();
                setServerError(null);
                setIsAdding(false);
              }}
            >
              Cancel
            </Button>
          </div>
        </form>
      )}

      {skills.length === 0 && !isAdding ? (
        <EmptyState label="No skills added yet." />
      ) : (
        <ul className="flex flex-wrap gap-2">
          {skills.map((studentSkill) => (
            <li
              key={studentSkill.id}
              className="flex items-center gap-2 rounded-full border border-zinc-200 bg-zinc-50 px-3 py-1.5 text-sm dark:border-zinc-800 dark:bg-zinc-900"
            >
              <span className="font-medium text-zinc-800 dark:text-zinc-100">{studentSkill.skill.name}</span>
              <span className="text-zinc-400 dark:text-zinc-500">
                · {proficiencyLabel[studentSkill.proficiency_level]}
              </span>
              <InlineConfirmButton
                label="✕"
                onConfirm={async () => {
                  await profileApi.removeSkill(studentSkill.id);
                  onChange();
                }}
              />
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}
