import { apiFetch } from "@/lib/api-client";
import type { LearningResource } from "@/types/learning";

export const learningApi = {
  list: (skillId?: string) =>
    apiFetch<LearningResource[]>(`/api/v1/learning-resources${skillId ? `?skill_id=${skillId}` : ""}`),
  get: (id: string) => apiFetch<LearningResource>(`/api/v1/learning-resources/${id}`),
};
