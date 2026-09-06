import { apiFetch } from "@/lib/api-client";
import type { CareerDetail, CareerListItem } from "@/types/career";

export const careerApi = {
  list: () => apiFetch<CareerListItem[]>("/api/v1/careers"),
  get: (id: string) => apiFetch<CareerDetail>(`/api/v1/careers/${id}`),
};
