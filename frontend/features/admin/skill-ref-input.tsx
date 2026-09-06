"use client";

import { useState } from "react";

import type { AdminSkillRef } from "@/types/admin";
import type { SkillCategory } from "@/types/profile";

const categoryOptions: { value: SkillCategory; label: string }[] = [
  { value: "technical", label: "Technical" },
  { value: "soft", label: "Soft skill" },
  { value: "programming_language", label: "Programming language" },
  { value: "framework", label: "Framework" },
  { value: "tool", label: "Tool" },
];

/** Shared across all four admin catalogue forms — every one of them tags
 * its entity with a list of (skill name, category) pairs, resolved
 * server-side via get_or_create rather than picked from existing ids, so
 * an admin can introduce a brand-new skill inline. */
export function SkillRefInput({
  label,
  value,
  onChange,
}: {
  label: string;
  value: AdminSkillRef[];
  onChange: (next: AdminSkillRef[]) => void;
}) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState<SkillCategory>("technical");

  const add = () => {
    const trimmed = name.trim();
    if (!trimmed) return;
    if (value.some((skill) => skill.name.toLowerCase() === trimmed.toLowerCase())) {
      setName("");
      return;
    }
    onChange([...value, { name: trimmed, category }]);
    setName("");
  };

  return (
    <div>
      <label className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">{label}</label>
      {value.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {value.map((skill) => (
            <span
              key={skill.name}
              className="flex items-center gap-1 rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
            >
              {skill.name}
              <button
                type="button"
                onClick={() => onChange(value.filter((s) => s.name !== skill.name))}
                className="text-zinc-400 hover:text-red-600 dark:hover:text-red-400"
                aria-label={`Remove ${skill.name}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-2">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              add();
            }
          }}
          placeholder="Skill name"
          className="flex-1 rounded-lg border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-900 outline-none placeholder:text-zinc-400 focus:border-zinc-400 focus:ring-2 focus:ring-zinc-900/10 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:placeholder:text-zinc-600 dark:focus:border-zinc-600"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value as SkillCategory)}
          className="rounded-lg border border-zinc-200 bg-white px-2 py-1.5 text-sm text-zinc-900 outline-none focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:focus:border-zinc-600"
        >
          {categoryOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={add}
          className="rounded-lg border border-zinc-200 px-3 py-1.5 text-sm text-zinc-600 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          Add
        </button>
      </div>
    </div>
  );
}
