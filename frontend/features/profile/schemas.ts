import { z } from "zod";

// Mirrors backend/app/schemas/profile.py — client-side validation is a UX
// layer only; the backend re-validates everything with the same rules.

const optionalUrl = z
  .string()
  .trim()
  .max(512)
  .refine((v) => v === "" || /^https?:\/\/.+/i.test(v), "Enter a full URL starting with http(s)://")
  .optional()
  .transform((v) => (v === "" ? undefined : v));

export const profileUpdateSchema = z.object({
  university: z.string().trim().max(255).optional().or(z.literal("")),
  degree: z.string().trim().max(255).optional().or(z.literal("")),
  semester: z.coerce.number().int().min(1).max(12).optional().or(z.literal("")),
  graduation_year: z.coerce.number().int().min(2000).max(2100).optional().or(z.literal("")),
  location: z.string().trim().max(255).optional().or(z.literal("")),
  bio: z.string().trim().max(2000).optional().or(z.literal("")),
  github_url: optionalUrl,
  linkedin_url: optionalUrl,
  portfolio_url: optionalUrl,
});
// react-hook-form manages the pre-coercion shape (form fields are always
// strings); the resolver hands onSubmit the post-coercion shape. zodResolver
// needs both generics — see each section's useForm<Input, any, Output> call.
export type ProfileUpdateInput = z.input<typeof profileUpdateSchema>;
export type ProfileUpdateOutput = z.output<typeof profileUpdateSchema>;

export const skillCategories: { value: string; label: string }[] = [
  { value: "technical", label: "Technical" },
  { value: "soft", label: "Soft skill" },
  { value: "programming_language", label: "Programming language" },
  { value: "framework", label: "Framework" },
  { value: "tool", label: "Tool" },
];

export const proficiencyLevels: { value: string; label: string }[] = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
  { value: "expert", label: "Expert" },
];

export const skillSchema = z.object({
  name: z.string().trim().min(1, "Enter a skill name.").max(100),
  category: z.enum(["technical", "soft", "programming_language", "framework", "tool"]),
  proficiency_level: z.enum(["beginner", "intermediate", "advanced", "expert"]),
});
export type SkillInput = z.input<typeof skillSchema>;
export type SkillOutput = z.output<typeof skillSchema>;

export const projectSchema = z
  .object({
    title: z.string().trim().min(1, "Enter a project title.").max(255),
    description: z.string().trim().max(4000).optional().or(z.literal("")),
    repo_url: optionalUrl,
    demo_url: optionalUrl,
    start_date: z.string().optional().or(z.literal("")),
    end_date: z.string().optional().or(z.literal("")),
    skill_ids: z.array(z.string()).default([]),
  })
  .refine((data) => !data.start_date || !data.end_date || data.end_date >= data.start_date, {
    message: "End date can't be before the start date.",
    path: ["end_date"],
  });
export type ProjectInput = z.input<typeof projectSchema>;
export type ProjectOutput = z.output<typeof projectSchema>;

export const employmentTypes: { value: string; label: string }[] = [
  { value: "internship", label: "Internship" },
  { value: "part_time", label: "Part-time" },
  { value: "full_time", label: "Full-time" },
  { value: "freelance", label: "Freelance" },
  { value: "volunteer", label: "Volunteer" },
];

export const experienceSchema = z
  .object({
    title: z.string().trim().min(1, "Enter a job title.").max(255),
    company: z.string().trim().min(1, "Enter a company name.").max(255),
    employment_type: z.enum(["internship", "part_time", "full_time", "freelance", "volunteer"]),
    start_date: z.string().min(1, "Enter a start date."),
    end_date: z.string().optional().or(z.literal("")),
    is_current: z.boolean().default(false),
    description: z.string().trim().max(4000).optional().or(z.literal("")),
  })
  .refine((data) => !data.end_date || data.end_date >= data.start_date, {
    message: "End date can't be before the start date.",
    path: ["end_date"],
  });
export type ExperienceInput = z.input<typeof experienceSchema>;
export type ExperienceOutput = z.output<typeof experienceSchema>;

export const certificationSchema = z.object({
  name: z.string().trim().min(1, "Enter a certification name.").max(255),
  issuer: z.string().trim().max(255).optional().or(z.literal("")),
  issue_date: z.string().optional().or(z.literal("")),
  credential_url: optionalUrl,
});
export type CertificationInput = z.input<typeof certificationSchema>;
export type CertificationOutput = z.output<typeof certificationSchema>;
