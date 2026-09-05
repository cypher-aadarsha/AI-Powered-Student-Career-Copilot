# Career Copilot — Frontend

Next.js 16 (App Router) + TypeScript + Tailwind CSS. See the repo root `README.md` for how to
run the full stack (frontend + backend + Postgres) via Docker Compose.

## Standalone commands

```bash
npm install
cp .env.example .env.local
npm run dev      # http://localhost:3000
npm run build    # production build + type check
npm run lint
```

**Docker note:** `NEXT_PUBLIC_API_URL` is inlined into the client bundle at build time, so under
Docker Compose it comes from `docker-compose.yml`'s `frontend.build.args`, not `.env.local`.
Changing it requires `docker compose build frontend`.

## Structure

```
app/          Routes (App Router) — login/, register/, me/ (Phase 3); more per phase
components/
  ui/          Small presentational primitives (button, text-field)
  layout/      Page shells (site-header, auth-shell)
features/      One folder per product module — auth/ (schemas + AuthProvider context) so far
hooks/         Shared React hooks — use-require-auth.ts guards a page client-side
lib/           Cross-cutting utilities — api-client.ts wraps every backend call and attaches
               the auth header; auth-token.ts is the only place that touches localStorage
types/         Shared TypeScript types for API response shapes
```

## Auth model (Phase 3)

The JWT the backend issues is stored in `localStorage` (see `lib/auth-token.ts`) and attached to
every `apiFetch` call as a bearer token. This is a client-side UX convenience only — route
guarding (`hooks/use-require-auth.ts`) redirects an unauthenticated visitor away from a protected
page, but the actual enforcement is the backend validating the JWT on every request. A `Next.js
proxy.ts` (server-side route guard) isn't used because it can't read `localStorage`; see the
Technical Design Document §18 for the accepted trade-off and what a cookie-based BFF alternative
would look like.
