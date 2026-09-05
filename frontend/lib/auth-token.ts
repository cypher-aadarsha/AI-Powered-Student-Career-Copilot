/**
 * Client-side token storage. This is a UX convenience only — it lets the
 * browser decide whether to show a logged-in state and whether to redirect
 * away from a protected page before a request round-trip. The actual
 * security boundary is the backend verifying the JWT on every request
 * (TDD §18); nothing here should ever be treated as authorization.
 */
const STORAGE_KEY = "career_copilot_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(STORAGE_KEY);
}

export function setToken(token: string): void {
  window.localStorage.setItem(STORAGE_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(STORAGE_KEY);
}

export function authHeader(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Decodes the JWT payload without verifying the signature — fine for a
 * client-side "should I bother calling /users/me" check, never for trust. */
export function isTokenExpired(token: string): boolean {
  try {
    const [, payloadSegment] = token.split(".");
    const payload = JSON.parse(atob(payloadSegment.replace(/-/g, "+").replace(/_/g, "/")));
    if (typeof payload.exp !== "number") return true;
    return Date.now() >= payload.exp * 1000;
  } catch {
    return true;
  }
}
