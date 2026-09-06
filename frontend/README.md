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
app/          Routes (App Router) — login/, register/ (Phase 3), profile/ (Phase 4), resume/ (Phase 5)
components/
  ui/          Small presentational primitives (button, text-field, textarea-field,
               select-field, inline-confirm-button)
  layout/      Page shells (site-header, auth-shell, section-card)
features/
  auth/        Zod schemas + AuthProvider context
  profile/     Zod schemas, api.ts (backend calls), use-profile.ts, and one component per
               profile section (skills/projects/experiences/certifications)
  resume/      api.ts (backend calls, including the multipart upload), use-resumes.ts,
               upload-form.tsx, resume-card.tsx (score bar, detected skills, strengths/
               suggestions)
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

## Profile page (Phase 4)

`/profile` composes five sections (core fields, skills, projects, experiences,
certifications), each with its own add/edit form and a two-step inline delete
(`InlineConfirmButton`) instead of a blocking `window.confirm()`. There's no cache/query
library yet — `features/profile/use-profile.ts` fetches on mount and every section's `onChange`
just refetches the whole profile; simple and fast enough at this data size. RHF + Zod forms use
the library's `useForm<Input, unknown, Output>` three-generic pattern wherever a schema coerces
or defaults a value (e.g. `semester` string → number), since the form's pre-submit shape and the
resolver's post-validation shape genuinely differ.

## Resume page (Phase 5)

`/resume` uploads a PDF/DOCX via `resumeApi.upload` (`features/resume/api.ts`) — a plain
`FormData` body with no `Content-Type` header set explicitly, so the browser attaches the
multipart boundary itself; `apiFetch` only ever adds the `Authorization` header unless told
otherwise, which is exactly what a file upload needs. Each resume card
(`features/resume/resume-card.tsx`) shows its parse status, a score bar, detected catalogue
skills, and AI-generated strengths/suggestions once `status` is `"parsed"`, with re-analyze and
two-step delete actions matching the profile page's `InlineConfirmButton` pattern.
