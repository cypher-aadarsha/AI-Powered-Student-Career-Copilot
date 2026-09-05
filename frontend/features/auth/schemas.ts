import { z } from "zod";

// Mirrors backend/app/schemas/auth.py — client-side validation is a UX
// layer only; the backend re-validates everything with the same rules.
export const registerSchema = z.object({
  full_name: z.string().min(1, "Enter your full name.").max(255),
  email: z.string().min(1, "Enter your email.").email("Enter a valid email address."),
  password: z.string().min(8, "Use at least 8 characters."),
});

export const loginSchema = z.object({
  email: z.string().min(1, "Enter your email.").email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
});

export type RegisterInput = z.infer<typeof registerSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
