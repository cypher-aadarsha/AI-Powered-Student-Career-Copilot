"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { JobListItem } from "@/types/job";
import { jobApi } from "./api";

interface JobsState {
  jobs: JobListItem[];
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount pattern as use-careers.ts — scores are recomputed
 * server-side on every fetch. */
export function useJobs() {
  const [state, setState] = useState<JobsState>({ jobs: [], isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const jobs = await jobApi.list();
      setState({ jobs, isLoading: false, error: null });
    } catch (err) {
      setState({
        jobs: [],
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load job matches.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
