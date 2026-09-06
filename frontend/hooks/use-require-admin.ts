"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/features/auth/auth-context";

/**
 * Same shape as use-require-auth.ts, but also bounces a logged-in non-admin
 * back to their dashboard. This is UX only — the real boundary is the
 * backend's require_role(UserRole.admin) on every /admin/* route, enforced
 * on every request regardless of what this hook does client-side.
 */
export function useRequireAdmin() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    if (!user) {
      router.replace("/login");
    } else if (user.role !== "admin") {
      router.replace("/");
    }
  }, [isLoading, user, router]);

  return { user, isLoading };
}
