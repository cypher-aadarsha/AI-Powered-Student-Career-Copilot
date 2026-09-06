"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { SectionCard } from "@/components/layout/section-card";
import { Button } from "@/components/ui/button";
import { ScoreBar } from "@/components/ui/score-bar";
import { useRequireAuth } from "@/hooks/use-require-auth";
import { interviewApi } from "@/features/interview/api";
import { ApiError } from "@/lib/api-client";
import type { InterviewQuestion, MockInterviewAnswer, MockInterviewSessionDetail } from "@/types/interview";

const categoryLabel: Record<string, string> = {
  behavioral: "Behavioral",
  technical: "Technical",
  situational: "Situational",
};

function AnswerForm({
  sessionId,
  question,
  onAnswered,
}: {
  sessionId: string;
  question: InterviewQuestion;
  onAnswered: () => void;
}) {
  const [answerText, setAnswerText] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await interviewApi.submitAnswer(sessionId, { question_id: question.id, answer_text: answerText });
      onAnswered();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't submit your answer. Try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mt-3 flex flex-col gap-2">
      <textarea
        value={answerText}
        onChange={(e) => setAnswerText(e.target.value)}
        rows={5}
        placeholder="Type your answer…"
        className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
      />
      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}
      <div>
        <Button
          type="button"
          onClick={handleSubmit}
          isLoading={isSubmitting}
          disabled={answerText.trim().length < 10}
        >
          Submit answer
        </Button>
      </div>
    </div>
  );
}

function AnsweredCard({ answer }: { answer: MockInterviewAnswer }) {
  return (
    <div className="mt-3 flex flex-col gap-3 rounded-lg bg-zinc-50 p-3 dark:bg-zinc-900">
      <p className="text-sm whitespace-pre-wrap text-zinc-600 dark:text-zinc-300">{answer.answer_text}</p>
      {answer.ai_score !== null && <ScoreBar score={answer.ai_score} />}
      {answer.ai_feedback && answer.ai_feedback.length > 0 && (
        <ul className="list-disc space-y-0.5 pl-4 text-sm text-zinc-600 dark:text-zinc-300">
          {answer.ai_feedback.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function InterviewSessionPage() {
  const { isLoading: isAuthLoading, user } = useRequireAuth();
  const params = useParams<{ id: string }>();
  const [session, setSession] = useState<MockInterviewSessionDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    try {
      const data = await interviewApi.getSession(params.id);
      setSession(data);
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load this session.");
    } finally {
      setIsLoading(false);
    }
  }, [params.id]);

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

  if (!user) return null; // useRequireAuth is already redirecting

  if (error || !session) {
    return (
      <div className="flex flex-1 items-center justify-center px-6">
        <div className="max-w-sm rounded-lg bg-red-50 px-4 py-3 text-center text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
          {error ?? "Session not found."}
        </div>
      </div>
    );
  }

  const answersByQuestionId = new Map(session.answers.map((answer) => [answer.question_id, answer]));

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-6 py-10">
      <div>
        <Link
          href="/interviews"
          className="text-xs font-medium text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
        >
          ← All mock interviews
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          {session.career_role ? session.career_role.title : "General mock interview"}
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          {session.status === "completed" ? "Completed" : "In progress"} · {session.answers.length}/
          {session.questions.length} answered
        </p>
        {session.average_score !== null && (
          <div className="mt-2">
            <ScoreBar score={session.average_score} />
          </div>
        )}
      </div>

      <SectionCard title="Questions">
        <ul className="flex flex-col gap-4">
          {session.questions.map((question, index) => {
            const answer = answersByQuestionId.get(question.id);
            return (
              <li key={question.id} className="rounded-lg border border-zinc-100 p-4 dark:border-zinc-800">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                    {index + 1}. {question.question_text}
                  </p>
                  <span className="shrink-0 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
                    {categoryLabel[question.category]}
                  </span>
                </div>
                {answer ? (
                  <AnsweredCard answer={answer} />
                ) : (
                  <AnswerForm sessionId={session.id} question={question} onAnswered={refetch} />
                )}
              </li>
            );
          })}
        </ul>
      </SectionCard>
    </div>
  );
}
