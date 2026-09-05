"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { TextField } from "@/components/ui/text-field";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { ApiError } from "@/lib/api-client";
import type { Certification } from "@/types/profile";
import { profileApi } from "./api";
import { certificationSchema, type CertificationInput, type CertificationOutput } from "./schemas";

function CertificationForm({
  initial,
  onCancel,
  onSaved,
}: {
  initial?: Certification;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [serverError, setServerError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CertificationInput, unknown, CertificationOutput>({
    resolver: zodResolver(certificationSchema),
    defaultValues: {
      name: initial?.name ?? "",
      issuer: initial?.issuer ?? "",
      issue_date: initial?.issue_date ?? "",
      credential_url: initial?.credential_url ?? "",
    },
  });

  const onSubmit = async (input: CertificationOutput) => {
    setServerError(null);
    try {
      if (initial) {
        await profileApi.updateCertification(initial.id, input);
      } else {
        await profileApi.addCertification(input);
      }
      onSaved();
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Couldn't save this certification. Try again.");
    }
  };

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="mb-4 grid grid-cols-1 gap-3 rounded-lg border border-zinc-100 p-4 sm:grid-cols-2 dark:border-zinc-800"
      noValidate
    >
      <TextField label="Name" error={errors.name?.message} {...register("name")} />
      <TextField label="Issuer" error={errors.issuer?.message} {...register("issuer")} />
      <TextField label="Issue date" type="date" error={errors.issue_date?.message} {...register("issue_date")} />
      <TextField
        label="Credential URL"
        placeholder="https://credential.example.com"
        error={errors.credential_url?.message}
        {...register("credential_url")}
      />
      {serverError && (
        <p role="alert" className="sm:col-span-2 text-sm text-red-600 dark:text-red-400">
          {serverError}
        </p>
      )}
      <div className="flex gap-2 sm:col-span-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Add certification"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export function CertificationsSection({
  certifications,
  onChange,
}: {
  certifications: Certification[];
  onChange: () => void;
}) {
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  return (
    <SectionCard
      title="Certifications"
      description="Courses and credentials you've completed."
      action={
        !isAdding && (
          <Button variant="ghost" onClick={() => setIsAdding(true)}>
            + Add certification
          </Button>
        )
      }
    >
      {isAdding && (
        <CertificationForm
          onCancel={() => setIsAdding(false)}
          onSaved={() => {
            setIsAdding(false);
            onChange();
          }}
        />
      )}

      {certifications.length === 0 && !isAdding ? (
        <EmptyState label="No certifications added yet." />
      ) : (
        <ul className="flex flex-col gap-3">
          {certifications.map((certification) =>
            editingId === certification.id ? (
              <li key={certification.id}>
                <CertificationForm
                  initial={certification}
                  onCancel={() => setEditingId(null)}
                  onSaved={() => {
                    setEditingId(null);
                    onChange();
                  }}
                />
              </li>
            ) : (
              <li
                key={certification.id}
                className="flex items-start justify-between gap-4 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800"
              >
                <div>
                  <h3 className="font-medium text-zinc-900 dark:text-zinc-50">{certification.name}</h3>
                  <p className="text-xs text-zinc-400">
                    {[certification.issuer, certification.issue_date].filter(Boolean).join(" · ")}
                  </p>
                  {certification.credential_url && (
                    <a
                      href={certification.credential_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-zinc-500 underline dark:text-zinc-400"
                    >
                      View credential
                    </a>
                  )}
                </div>
                <div className="flex shrink-0 gap-3">
                  <button
                    type="button"
                    onClick={() => setEditingId(certification.id)}
                    className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                  >
                    Edit
                  </button>
                  <InlineConfirmButton
                    onConfirm={async () => {
                      await profileApi.deleteCertification(certification.id);
                      onChange();
                    }}
                  />
                </div>
              </li>
            )
          )}
        </ul>
      )}
    </SectionCard>
  );
}
