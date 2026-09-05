import type { ReactNode } from "react";
import Link from "next/link";

export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: { prompt: string; linkLabel: string; href: string };
}) {
  return (
    <div className="flex flex-1 items-center justify-center bg-zinc-50 px-6 py-16 dark:bg-black">
      <div className="w-full max-w-sm">
        <p className="mb-6 text-center text-sm font-semibold tracking-wide text-zinc-400 uppercase">
          Career Copilot
        </p>
        <div className="rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
          <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">{title}</h1>
          <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">{subtitle}</p>
          <div className="mt-6">{children}</div>
        </div>
        <p className="mt-6 text-center text-sm text-zinc-500 dark:text-zinc-400">
          {footer.prompt}{" "}
          <Link href={footer.href} className="font-medium text-zinc-900 underline dark:text-zinc-100">
            {footer.linkLabel}
          </Link>
        </p>
      </div>
    </div>
  );
}
