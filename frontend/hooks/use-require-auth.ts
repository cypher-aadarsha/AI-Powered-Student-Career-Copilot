"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/features/auth/auth-context";

/**
 * Client-side route guard: redirects to /login once we know there's no
 * session. This is UX only, not enforcement — every API call still requires
 * a valid JWT server-side regardless of whether this hook ran (TDD §18).
 */
export function useRequireAuth() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  return { user, isLoading };
}
