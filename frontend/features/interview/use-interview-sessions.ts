"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { MockInterviewSessionSummary } from "@/types/interview";
import { interviewApi } from "./api";

interface SessionsState {
  sessions: MockInterviewSessionSummary[];
  isLoading: boolean;
  error: string | null;
}

/** Same fetch-on-mount pattern as the other list hooks. */
export function useInterviewSessions() {
  const [state, setState] = useState<SessionsState>({ sessions: [], isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const sessions = await interviewApi.listSessions();
      setState({ sessions, isLoading: false, error: null });
    } catch (err) {
      setState({
        sessions: [],
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load your mock interviews.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
