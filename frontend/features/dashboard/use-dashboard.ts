"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { DashboardData } from "@/types/dashboard";
import { dashboardApi } from "./api";

interface DashboardState {
  dashboard: DashboardData | null;
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount pattern as every other list/detail hook in the app. */
export function useDashboard() {
  const [state, setState] = useState<DashboardState>({ dashboard: null, isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const dashboard = await dashboardApi.get();
      setState({ dashboard, isLoading: false, error: null });
    } catch (err) {
      setState({
        dashboard: null,
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load your dashboard.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
