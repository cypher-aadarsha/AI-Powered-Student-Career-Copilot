import { apiFetch } from "@/lib/api-client";
import type { CareerDetail, CareerListItem } from "@/types/career";
import type { RoleLearningPlan } from "@/types/learning";

export const careerApi = {
  list: () => apiFetch<CareerListItem[]>("/api/v1/careers"),
  get: (id: string) => apiFetch<CareerDetail>(`/api/v1/careers/${id}`),
  getLearningPlan: (id: string) => apiFetch<RoleLearningPlan>(`/api/v1/careers/${id}/learning-plan`),
};
