import { apiFetch } from "@/lib/api-client";
import type { Certification, Experience, Project, StudentProfile, StudentSkill } from "@/types/profile";
import type {
  CertificationOutput,
  ExperienceOutput,
  ProfileUpdateOutput,
  ProjectOutput,
  SkillOutput,
} from "./schemas";

const json = (body: unknown): RequestInit => ({
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

/** Blank-string form fields mean "not set" — normalize to null before the
 * request leaves the browser rather than asking the backend to guess. */
function blankToNull<T extends Record<string, unknown>>(input: T): T {
  const out: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(input)) {
    out[key] = value === "" ? null : value;
  }
  return out as T;
}

export const profileApi = {
  get: () => apiFetch<StudentProfile>("/api/v1/profile"),

  update: (input: ProfileUpdateOutput) =>
    apiFetch<StudentProfile>("/api/v1/profile", { method: "PUT", ...json(blankToNull(input)) }),

  addSkill: (input: SkillOutput) =>
    apiFetch<StudentSkill>("/api/v1/profile/skills", { method: "POST", ...json(input) }),
  removeSkill: (id: string) => apiFetch<void>(`/api/v1/profile/skills/${id}`, { method: "DELETE" }),

  addProject: (input: ProjectOutput) =>
    apiFetch<Project>("/api/v1/profile/projects", { method: "POST", ...json(blankToNull(input)) }),
  updateProject: (id: string, input: ProjectOutput) =>
    apiFetch<Project>(`/api/v1/profile/projects/${id}`, { method: "PUT", ...json(blankToNull(input)) }),
  deleteProject: (id: string) => apiFetch<void>(`/api/v1/profile/projects/${id}`, { method: "DELETE" }),

  addExperience: (input: ExperienceOutput) =>
    apiFetch<Experience>("/api/v1/profile/experiences", { method: "POST", ...json(blankToNull(input)) }),
  updateExperience: (id: string, input: ExperienceOutput) =>
    apiFetch<Experience>(`/api/v1/profile/experiences/${id}`, { method: "PUT", ...json(blankToNull(input)) }),
  deleteExperience: (id: string) => apiFetch<void>(`/api/v1/profile/experiences/${id}`, { method: "DELETE" }),

  addCertification: (input: CertificationOutput) =>
    apiFetch<Certification>("/api/v1/profile/certifications", { method: "POST", ...json(blankToNull(input)) }),
  updateCertification: (id: string, input: CertificationOutput) =>
    apiFetch<Certification>(`/api/v1/profile/certifications/${id}`, { method: "PUT", ...json(blankToNull(input)) }),
  deleteCertification: (id: string) =>
    apiFetch<void>(`/api/v1/profile/certifications/${id}`, { method: "DELETE" }),
};
