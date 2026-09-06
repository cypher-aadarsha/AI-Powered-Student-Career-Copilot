import { apiFetch } from "@/lib/api-client";
import type { MockInterviewAnswer, MockInterviewSessionDetail, MockInterviewSessionSummary } from "@/types/interview";

const json = (body: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const interviewApi = {
  listSessions: () => apiFetch<MockInterviewSessionSummary[]>("/api/v1/interviews/sessions"),
  getSession: (id: string) => apiFetch<MockInterviewSessionDetail>(`/api/v1/interviews/sessions/${id}`),

  startSession: (input: { career_role_id?: string; question_count?: number }) =>
    apiFetch<MockInterviewSessionDetail>("/api/v1/interviews/sessions", { method: "POST", ...json(input) }),

  submitAnswer: (sessionId: string, input: { question_id: string; answer_text: string }) =>
    apiFetch<MockInterviewAnswer>(`/api/v1/interviews/sessions/${sessionId}/answers`, {
      method: "POST",
      ...json(input),
    }),
};
