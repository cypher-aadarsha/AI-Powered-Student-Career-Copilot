"use client";

import { useState } from "react";

/** Two-step delete: click once to arm, click again to confirm. Avoids a
 * blocking window.confirm() dialog while still preventing a stray click
 * from deleting something. */
export function InlineConfirmButton({
  onConfirm,
  label = "Delete",
  confirmLabel = "Confirm?",
}: {
  onConfirm: () => Promise<void> | void;
  label?: string;
  confirmLabel?: string;
}) {
  const [armed, setArmed] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!armed) {
    return (
      <button
        type="button"
        onClick={() => setArmed(true)}
        className="text-xs font-medium text-zinc-400 hover:text-red-600 dark:hover:text-red-400"
      >
        {label}
      </button>
    );
  }

  return (
    <span className="flex items-center gap-2">
      <button
        type="button"
        disabled={isDeleting}
        onClick={async () => {
          setIsDeleting(true);
          await onConfirm();
        }}
        className="text-xs font-medium text-red-600 hover:text-red-700 disabled:opacity-60 dark:text-red-400"
      >
        {isDeleting ? "Deleting…" : confirmLabel}
      </button>
      <button
        type="button"
        onClick={() => setArmed(false)}
        className="text-xs text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
      >
        Cancel
      </button>
    </span>
  );
}
