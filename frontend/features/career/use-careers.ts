"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { CareerListItem } from "@/types/career";
import { careerApi } from "./api";

interface CareersState {
  careers: CareerListItem[];
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount pattern as use-profile.ts / use-resumes.ts. Scores
 * are recomputed server-side on every fetch, so a plain refetch after a
 * profile edit is enough to reflect it — no client-side recomputation. */
export function useCareers() {
  const [state, setState] = useState<CareersState>({ careers: [], isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const careers = await careerApi.list();
      setState({ careers, isLoading: false, error: null });
    } catch (err) {
      setState({
        careers: [],
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load career matches.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
