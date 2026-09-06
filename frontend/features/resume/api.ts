import { apiFetch } from "@/lib/api-client";
import type { Resume } from "@/types/resume";

export const resumeApi = {
  list: () => apiFetch<Resume[]>("/api/v1/resumes"),

  // No Content-Type header here on purpose — the browser sets
  // multipart/form-data with the correct boundary itself; apiFetch only
  // ever adds the Authorization header unless we override it.
  upload: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch<Resume>("/api/v1/resumes", { method: "POST", body: formData });
  },

  reanalyze: (id: string) => apiFetch<Resume>(`/api/v1/resumes/${id}/reanalyze`, { method: "POST" }),
  remove: (id: string) => apiFetch<void>(`/api/v1/resumes/${id}`, { method: "DELETE" }),
};
