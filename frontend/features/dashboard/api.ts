import { apiFetch } from "@/lib/api-client";
import type { DashboardData } from "@/types/dashboard";

export const dashboardApi = {
  get: () => apiFetch<DashboardData>("/api/v1/dashboard"),
};
