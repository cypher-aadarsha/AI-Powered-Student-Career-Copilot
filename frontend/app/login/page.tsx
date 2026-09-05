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
import { loginSchema, type LoginInput } from "@/features/auth/schemas";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (input: LoginInput) => {
    setServerError(null);
    try {
      await login(input);
      router.push("/me");
    } catch (err) {
      setServerError(err instanceof ApiError ? err.message : "Something went wrong. Try again.");
    }
  };

  return (
    <AuthShell
      title="Log in"
      subtitle="Welcome back — pick up where you left off."
      footer={{ prompt: "New here?", linkLabel: "Create an account", href: "/register" }}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4" noValidate>
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
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />
        {serverError && (
          <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-400">
            {serverError}
          </p>
        )}
        <Button type="submit" isLoading={isSubmitting} className="mt-2 w-full">
          Log in
        </Button>
      </form>
    </AuthShell>
  );
}
