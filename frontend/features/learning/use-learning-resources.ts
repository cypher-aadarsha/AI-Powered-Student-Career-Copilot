"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { LearningResource } from "@/types/learning";
import { learningApi } from "./api";

interface LearningResourcesState {
  resources: LearningResource[];
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount pattern as the other list hooks. Re-fetches whenever
 * `skillId` changes so clicking a skill filter re-queries the backend
 * rather than filtering a client-side cache. */
export function useLearningResources(skillId?: string) {
  const [state, setState] = useState<LearningResourcesState>({ resources: [], isLoading: true, error: null });

  const refetch = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true }));
    try {
      const resources = await learningApi.list(skillId);
      setState({ resources, isLoading: false, error: null });
    } catch (err) {
      setState({
        resources: [],
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load learning resources.",
      });
    }
  }, [skillId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount/filter-change; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
