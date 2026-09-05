/**
 * Thin fetch wrapper. Every backend call in the app goes through here so
 * error normalization and the base-URL split (browser vs. server-side,
 * see below) live in exactly one place.
 */
import { authHeader } from "./auth-token";

// Server components/route handlers run inside the Docker network and must
// reach the backend by its service name; the browser reaches it via the
// published port. Both default to sane localhost values for non-Docker dev.
function getApiBaseUrl(): string {
  const isServer = typeof window === "undefined";
  if (isServer) {
    return process.env.API_INTERNAL_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const response = await fetch(url, {
    ...init,
    cache: "no-store",
    headers: { ...authHeader(), ...init?.headers },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.error?.message ?? `Request to ${path} failed with status ${response.status}`;
    throw new ApiError(response.status, message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json();
  return body.data as T;
}
