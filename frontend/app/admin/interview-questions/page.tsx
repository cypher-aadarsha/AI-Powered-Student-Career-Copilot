"use client";

import Link from "next/link";
import { useCallback, useEffect, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { InlineConfirmButton } from "@/components/ui/inline-confirm-button";
import { EmptyState, SectionCard } from "@/components/layout/section-card";
import { useRequireAdmin } from "@/hooks/use-require-admin";
import { adminApi } from "@/features/admin/api";
import { SkillRefInput } from "@/features/admin/skill-ref-input";
import { ApiError } from "@/lib/api-client";
import type { AdminInterviewQuestion, AdminInterviewQuestionInput, AdminSkillRef } from "@/types/admin";
import type { QuestionCategory, QuestionDifficulty } from "@/types/interview";

const categories: { value: QuestionCategory; label: string }[] = [
  { value: "behavioral", label: "Behavioral" },
  { value: "technical", label: "Technical" },
  { value: "situational", label: "Situational" },
];

const difficulties: { value: QuestionDifficulty; label: string }[] = [
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
];

const emptyForm: AdminInterviewQuestionInput = {
  question_text: "",
  category: "behavioral",
  difficulty: "easy",
  model_answer: "",
  skills: [],
};

function toInput(question: AdminInterviewQuestion): AdminInterviewQuestionInput {
  return {
    question_text: question.question_text,
    category: question.category,
    difficulty: question.difficulty,
    model_answer: question.model_answer,
    skills: question.skills.map((s) => ({ name: s.name, category: s.category })),
  };
}

function QuestionForm({
  initial,
  onCancel,
  onSaved,
}: {
  initial?: AdminInterviewQuestion;
  onCancel: () => void;
  onSaved: () => void;
}) {
  const [form, setForm] = useState<AdminInterviewQuestionInput>(initial ? toInput(initial) : emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = { ...form, model_answer: form.model_answer || null };
      if (initial) {
        await adminApi.updateInterviewQuestion(initial.id, payload);
      } else {
        await adminApi.createInterviewQuestion(payload);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save this question. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mb-4 flex flex-col gap-3 rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
      <div>
        <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Question</label>
        <textarea
          required
          value={form.question_text}
          onChange={(e) => setForm({ ...form, question_text: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
      </div>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Category</label>
          <select
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value as QuestionCategory })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          >
            {categories.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">Difficulty</label>
          <select
            value={form.difficulty}
            onChange={(e) => setForm({ ...form, difficulty: e.target.value as QuestionDifficulty })}
            className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
          >
            {difficulties.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
          Model answer <span className="font-normal text-zinc-400">(used only for AI feedback scoring, never shown to students before they answer)</span>
        </label>
        <textarea
          value={form.model_answer ?? ""}
          onChange={(e) => setForm({ ...form, model_answer: e.target.value })}
          rows={2}
          className="w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50"
        />
      </div>
      <SkillRefInput label="Skills probed" value={form.skills} onChange={(next: AdminSkillRef[]) => setForm({ ...form, skills: next })} />
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <div className="flex gap-2">
        <Button type="submit" isLoading={isSubmitting}>
          {initial ? "Save changes" : "Create question"}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}

export default function AdminInterviewQuestionsPage() {
  const { isLoading: isAuthLoading, user } = useRequireAdmin();
  const [questions, setQuestions] = useState<AdminInterviewQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await adminApi.listInterviewQuestions();
      setQuestions(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load interview questions.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!user) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [user, refetch]);

  if (isAuthLoading || (user && isLoading)) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-500 dark:text-zinc-400">Loading…</p>
      </div>
    );
  }

  if (!user || user.role !== "admin") return null; // useRequireAdmin is already redirecting

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <Link href="/admin" className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200">
          ← Admin panel
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">Interview questions</h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">The bank mock interview sessions draw from.</p>
      </div>

      <SectionCard
        title={`${questions.length} question${questions.length === 1 ? "" : "s"}`}
        action={
          !isAdding && (
            <Button variant="ghost" onClick={() => setIsAdding(true)}>
              + Add question
            </Button>
          )
        }
      >
        {error && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
        {deleteError && <p className="mb-3 text-sm text-red-600 dark:text-red-400">{deleteError}</p>}
        {isAdding && (
          <QuestionForm
            onCancel={() => setIsAdding(false)}
            onSaved={() => {
              setIsAdding(false);
              refetch();
            }}
          />
        )}
        {questions.length === 0 && !isAdding ? (
          <EmptyState label="No interview questions yet." />
        ) : (
          <ul className="flex flex-col gap-3">
            {questions.map((question) =>
              editingId === question.id ? (
                <li key={question.id}>
                  <QuestionForm
                    initial={question}
                    onCancel={() => setEditingId(null)}
                    onSaved={() => {
                      setEditingId(null);
                      refetch();
                    }}
                  />
                </li>
              ) : (
                <li key={question.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{question.question_text}</p>
                      <p className="mt-0.5 text-xs text-zinc-400">
                        {question.category} · {question.difficulty}
                      </p>
                    </div>
                    <div className="flex shrink-0 gap-3">
                      <button
                        type="button"
                        onClick={() => setEditingId(question.id)}
                        className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
                      >
                        Edit
                      </button>
                      <InlineConfirmButton
                        onConfirm={async () => {
                          setDeleteError(null);
                          try {
                            await adminApi.deleteInterviewQuestion(question.id);
                            refetch();
                          } catch (err) {
                            setDeleteError(err instanceof ApiError ? err.message : "Couldn't delete this question.");
                          }
                        }}
                      />
                    </div>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {question.skills.map((s) => (
                      <span key={s.id} className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300">
                        {s.name}
                      </span>
                    ))}
                  </div>
                </li>
              )
            )}
          </ul>
        )}
      </SectionCard>
    </div>
  );
}
