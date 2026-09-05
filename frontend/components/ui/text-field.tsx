import { forwardRef, type InputHTMLAttributes } from "react";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, id, ...props }, ref) => {
    const fieldId = id ?? props.name;
    return (
      <div className="flex flex-col gap-1.5">
        <label htmlFor={fieldId} className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
          {label}
        </label>
        <input
          ref={ref}
          id={fieldId}
          className={`rounded-lg border px-3 py-2 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 focus:ring-2 focus:ring-zinc-900/10 dark:text-zinc-50 dark:placeholder:text-zinc-600 ${
            error
              ? "border-red-400 focus:border-red-500"
              : "border-zinc-200 focus:border-zinc-400 dark:border-zinc-800 dark:focus:border-zinc-600"
          } bg-white dark:bg-zinc-900`}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${fieldId}-error` : undefined}
          {...props}
        />
        {error && (
          <p id={`${fieldId}-error`} className="text-xs text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);
TextField.displayName = "TextField";
