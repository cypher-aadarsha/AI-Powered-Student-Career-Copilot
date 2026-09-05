"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/features/auth/auth-context";

export function SiteHeader() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  return (
    <header className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
      <Link href="/" className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
        Career Copilot
      </Link>
      <nav className="flex items-center gap-4 text-sm">
        {isLoading ? null : user ? (
          <>
            <Link href="/profile" className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-50">
              {user.full_name}
            </Link>
            <button
              onClick={async () => {
                await logout();
                router.push("/login");
              }}
              className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-50"
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link href="/login" className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-300 dark:hover:text-zinc-50">
              Log in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-zinc-900 px-3 py-1.5 font-medium text-zinc-50 hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
            >
              Sign up
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}
