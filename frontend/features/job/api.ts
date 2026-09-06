import { apiFetch } from "@/lib/api-client";
import type { JobDetail, JobListItem } from "@/types/job";

export const jobApi = {
  list: () => apiFetch<JobListItem[]>("/api/v1/jobs"),
  get: (id: string) => apiFetch<JobDetail>(`/api/v1/jobs/${id}`),
};
