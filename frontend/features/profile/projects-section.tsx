"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { TextField } from "@/components/ui/text-field";
import { TextareaField } from "@/components/ui/textarea-field";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ApiError } from "@/lib/api-client";
import type { Project, StudentSkill } from "@/types/profile";
import { profileApi } from "./api";
import { projectSchema, type ProjectInput, type ProjectOutput } from "./schemas";

function ProjectForm({
  initial,
  availableSkills,
  onCancel,
  onSaved,
}: {
  initial?: Project;
  availableSkills: StudentSkill[];
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProjectInput, unknown, ProjectOutput>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      title: initial?.title ?? "",
      description: initial?.description ?? "",
      repo_url: initial?.repo_url ?? "",
      demo_url: initial?.demo_url ?? "",
      start_date: initial?.start_date ?? "",
      end_date: initial?.end_date ?? "",
      skill_ids: initial?.skills.map((s) => s.id) ?? [],
    },
  });

  const onSubmit = async (input: ProjectOutput) => {
    setServerError(null);
    try {
      if (initial) {
        await profileApi.updateProject(initial.id, input);
      } else {
        await profileApi.addProject(input);
      }
      onSaved();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Couldn't save this project. Try again.");
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="mb-4 flex flex-col gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800"
      noValidate
    >
      <TextField label="Title" error={errors.title?.message} {...register("title")} />
      <TextareaField label="Description" error={errors.description?.message} {...register("description")} />
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <TextField
          label="Repository URL"
          placeholder="https://github.com/you/project"
          error={errors.repo_url?.message}
          {...register("repo_url")}
        />
        <TextField
          label="Live demo URL"
          placeholder="https://project.dev"
          error={errors.demo_url?.message}
          {...register("demo_url")}
        />
        <TextField label="Start date" type="date" error={errors.start_date?.message} {...register("start_date")} />
        <TextField label="End date" type="date" error={errors.end_date?.message} {...register("end_date")} />
      </div>

      {availableSkills.length > 0 && (
        <fieldset>
          <legend className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Skills used</legend>
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2">
            {availableSkills.map((s) => (
              <label key={s.id} className="flex items-center gap-1.5 text-sm text-zinc-600 dark:text-zinc-300">
                <input type="checkbox" value={s.skill.id} {...register("skill_ids")} className="rounded" />
                {s.skill.name}
              </label>
            ))}
          </div>
          <p className="mt-1 text-xs text-zinc-400">Add skills to your profile first to tag them here.</p>
        </fieldset>
      )}

      {serverError && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {serverError}
        </p>
      )}

      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Add project"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export function ProjectsSection({
  projects,
  availableSkills,
  onChange,
}: {
  projects: Project[];
  availableSkills: StudentSkill[];
  onChange: () => void;
}) {
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  return (
    <SectionCard
      title="Projects"
      description="What you've built, with links and the skills each one demonstrates."
      action={
        !isAdding && (
          <Button variant="ghost" onClick={() => setIsAdding(true)}>
            + Add project
          </Button>
        )
      }
    >
      {isAdding && (
        <ProjectForm
          availableSkills={availableSkills}
          onCancel={() => setIsAdding(false)}
          onSaved={() => {
            setIsAdding(false);
            onChange();
          }}
        />
      )}

      {projects.length === 0 && !isAdding ? (
        <EmptyState label="No projects added yet." />
      ) : (
        <ul className="flex flex-col gap-3">
          {projects.map((project) =>
            editingId === project.id ? (
              <li key={project.id}>
                <ProjectForm
                  initial={project}
                  availableSkills={availableSkills}
                  onCancel={() => setEditingId(null)}
                  onSaved={() => {
                    setEditingId(null);
                    onChange();
                  }}
                />
              </li>
            ) : (
              <li key={project.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                <div className="flex items-start justify-between gap-4">
                  <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{project.title}</h3>
                  <div className="flex shrink-0 gap-3">
                    <button
                      type="button"
                      onClick={() => setEditingId(project.id)}
                      className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                    >
                      Edit
                    </button>
                    <InlineConfirmButton
                      onConfirm={async () => {
                        await profileApi.deleteProject(project.id);
                        onChange();
                      }}
                    />
                  </div>
                </div>
                {project.description && (
                  <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{project.description}</p>
                )}
                {project.skills.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {project.skills.map((s) => (
                      <span
                        key={s.id}
                        className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                )}
                <div className="mt-2 flex gap-3 text-xs">
                  {project.repo_url && (
                    <a href={project.repo_url} target="_blank" rel="noreferrer" className="text-zinc-500 underline dark:text-zinc-400">
                      Repository
                    </a>
                  )}
                  {project.demo_url && (
                    <a href={project.demo_url} target="_blank" rel="noreferrer" className="text-zinc-500 underline dark:text-zinc-400">
                      Live demo
                    </a>
                  )}
                </div>
              </li>
            )
          )}
        </ul>
      )}
    </SectionCard>
  );
}
