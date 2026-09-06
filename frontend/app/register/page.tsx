"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { AuthShell } from "@/components/layout/auth-shell";
import { Button } from "@/components/ui/button";
import { TextField } from "@/components/ui/text-field";
import { ApiError } from "@/lib/api-client";
import { useAuth } from "@/features/auth/auth-context";
import { registerSchema, type RegisterInput } from "@/features/auth/schemas";

export default function RegisterPage() {
  const { register: registerAccount, login } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterInput>({ resolver: zodResolver(registerSchema) });

  const onSubmit = async (input: RegisterInput) => {
    setServerError(null);
    try {
      await registerAccount(input);
      // Registration doesn't return a session — log the new account in
      // immediately so the flow feels like one step, not two.
      await login({ email: input.email, password: input.password });
      router.push("/");
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    }
  };

  return (
    <AuthShell
      title="Create your account"
      subtitle="Start tracking your career readiness."
      footer={{ prompt: "Already have an account?", linkLabel: "Log in", href: "/login" }}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
        <TextField
          label="Full name"
          autoComplete="name"
          error={errors.full_name?.message}
          {...register("full_name")}
        />
        <TextField
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <TextField
          label="Password"
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {serverError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
            {serverError}
          </p>
        )}
        <Button type="submit" isLoading={isSubmitting} className="mt-2 w-full">
          Create account
        </Button>
      </form>
    </AuthShell>
  );
}
