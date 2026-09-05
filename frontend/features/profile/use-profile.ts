"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError } from "@/lib/api-client";
import type { StudentProfile } from "@/types/profile";
import { profileApi } from "./api";

interface ProfileState {
  profile: StudentProfile | null;
  isLoading: boolean;
  error: string | null;
}

/** Fetch-on-mount + refetch-after-mutation. No optimistic updates or cache
 * library — the profile page is a single view with infrequent writes, so
 * "mutate, then re-pull the source of truth" is simpler and just as fast. */
export function useProfile() {
  const [state, setState] = useState<ProfileState>({ profile: null, isLoading: true, error: null });

  const refetch = useCallback(async () => {
    try {
      const profile = await profileApi.get();
      setState({ profile, isLoading: false, error: null });
    } catch (err) {
      setState({
        profile: null,
        isLoading: false,
        error: err instanceof ApiError ? err.message : "Could not load your profile.",
      });
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- fetch-on-mount; setState happens after the await inside refetch, not synchronously here.
    refetch();
  }, [refetch]);

  return { ...state, refetch };
}
