"use client";

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

import { apiFetch } from "@/lib/api-client";
import { clearToken, getToken, isTokenExpired, setToken } from "@/lib/auth-token";
import type { CurrentUser, TokenData } from "@/types/auth";
import type { LoginInput, RegisterInput } from "./schemas";

interface AuthContextValue {
  user: CurrentUser | null;
  isLoading: boolean;
  login: (input: LoginInput) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadCurrentUser = useCallback(async () => {
    const token = getToken();
    if (!token || isTokenExpired(token)) {
      clearToken();
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const me = await apiFetch<CurrentUser>("/api/v1/users/me");
      setUser(me);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Reading the persisted session on mount is the "synchronize with an
    // external system" case effects exist for (localStorage + the backend's
    // /users/me) — the actual setState calls inside loadCurrentUser happen
    // after an await, not synchronously in this effect body.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadCurrentUser();
  }, [loadCurrentUser]);

  const login = useCallback(
    async (input: LoginInput) => {
      const token = await apiFetch<TokenData>("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
      });
      setToken(token.access_token);
      await loadCurrentUser();
    },
    [loadCurrentUser]
  );

  const register = useCallback(async (input: RegisterInput) => {
    await apiFetch<CurrentUser>("/api/v1/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiFetch<void>("/api/v1/auth/logout", { method: "POST" });
    } finally {
      clearToken();
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
