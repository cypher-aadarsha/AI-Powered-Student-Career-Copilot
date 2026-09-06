import { apiFetch } from "@/lib/api-client";
import type {
  AdminCareerRole,
  AdminCareerRoleInput,
  AdminInterviewQuestion,
  AdminInterviewQuestionInput,
  AdminJobPosting,
  AdminJobPostingInput,
  AdminLearningResourceInput,
  AdminUser,
} from "@/types/admin";
import type { LearningResource } from "@/types/learning";

const json = (body: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const adminApi = {
  listUsers: () => apiFetch<AdminUser[]>("/api/v1/admin/users"),
  setUserActive: (id: string, is_active: boolean) =>
    apiFetch<AdminUser>(`/api/v1/admin/users/${id}`, { method: "PATCH", ...json({ is_active }) }),

  listCareerRoles: () => apiFetch<AdminCareerRole[]>("/api/v1/admin/career-roles"),
  createCareerRole: (input: AdminCareerRoleInput) =>
    apiFetch<AdminCareerRole>("/api/v1/admin/career-roles", { method: "POST", ...json(input) }),
  updateCareerRole: (id: string, input: AdminCareerRoleInput) =>
    apiFetch<AdminCareerRole>(`/api/v1/admin/career-roles/${id}`, { method: "PUT", ...json(input) }),
  deleteCareerRole: (id: string) => apiFetch<void>(`/api/v1/admin/career-roles/${id}`, { method: "DELETE" }),

  listLearningResources: () => apiFetch<LearningResource[]>("/api/v1/admin/learning-resources"),
  createLearningResource: (input: AdminLearningResourceInput) =>
    apiFetch<LearningResource>("/api/v1/admin/learning-resources", { method: "POST", ...json(input) }),
  updateLearningResource: (id: string, input: AdminLearningResourceInput) =>
    apiFetch<LearningResource>(`/api/v1/admin/learning-resources/${id}`, { method: "PUT", ...json(input) }),
  deleteLearningResource: (id: string) => apiFetch<void>(`/api/v1/admin/learning-resources/${id}`, { method: "DELETE" }),

  listJobPostings: () => apiFetch<AdminJobPosting[]>("/api/v1/admin/job-postings"),
  createJobPosting: (input: AdminJobPostingInput) =>
    apiFetch<AdminJobPosting>("/api/v1/admin/job-postings", { method: "POST", ...json(input) }),
  updateJobPosting: (id: string, input: AdminJobPostingInput) =>
    apiFetch<AdminJobPosting>(`/api/v1/admin/job-postings/${id}`, { method: "PUT", ...json(input) }),
  deleteJobPosting: (id: string) => apiFetch<void>(`/api/v1/admin/job-postings/${id}`, { method: "DELETE" }),

  listInterviewQuestions: () => apiFetch<AdminInterviewQuestion[]>("/api/v1/admin/interview-questions"),
  createInterviewQuestion: (input: AdminInterviewQuestionInput) =>
    apiFetch<AdminInterviewQuestion>("/api/v1/admin/interview-questions", { method: "POST", ...json(input) }),
  updateInterviewQuestion: (id: string, input: AdminInterviewQuestionInput) =>
    apiFetch<AdminInterviewQuestion>(`/api/v1/admin/interview-questions/${id}`, { method: "PUT", ...json(input) }),
  deleteInterviewQuestion: (id: string) => apiFetch<void>(`/api/v1/admin/interview-questions/${id}`, { method: "DELETE" }),
};
