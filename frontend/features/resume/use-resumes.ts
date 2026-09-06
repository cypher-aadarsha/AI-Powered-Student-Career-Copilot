"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { Resume } from "@/types/resume";
import { resumeApi } from "./api";

interface ResumesState {
  resumes: Resume[];
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount + refetch-after-mutation pattern as use-profile.ts —
 * infrequent writes, no cache library needed at this scale. */
export function useResumes() {
  const [state, setState] = useState<ResumesState>({ resumes: [], isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const resumes = await resumeApi.list();
      setState({ resumes, isLoading: false, error: null });
    } catch (err) {
      setState({
        resumes: [],
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load your resumes.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
