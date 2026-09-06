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
app/          Routes (App Router) — page.tsx is the dashboard (Phase 9, protected — see below);
               login/, register/ (Phase 3), profile/ (Phase 4), resume/ (Phase 5),
               careers/ + careers/[id]/ (Phase 6), jobs/ + jobs/[id]/, learning/ (Phase 7),
               interviews/ + interviews/[id]/ (Phase 8), admin/ + four admin/<catalogue>/
               sub-pages + admin/users/ (Phase 10, protected by role — see below)
components/
  ui/          Small presentational primitives (button, text-field, textarea-field,
               select-field, inline-confirm-button, score-bar — shared by resume, careers,
               jobs & interviews; progress-ring and stat-card are dashboard-only so far)
  layout/      Page shells (site-header, auth-shell, section-card)
features/
  auth/        Zod schemas + AuthProvider context
  profile/     Zod schemas, api.ts (backend calls), use-profile.ts, and one component per
               profile section (skills/projects/experiences/certifications)
  resume/      api.ts (backend calls, including the multipart upload), use-resumes.ts,
               upload-form.tsx, resume-card.tsx (score bar, detected skills, strengths/
               suggestions)
  career/      api.ts (includes getLearningPlan, called from the careers/[id] page),
               use-careers.ts — the list page's data layer
  job/         api.ts, use-jobs.ts — same shape as career/, the detail page fetches inline
  learning/    api.ts, use-learning-resources.ts (re-fetches on skill filter change)
  interview/   api.ts, use-interview-sessions.ts — the list page's data layer; the session
               detail page fetches (and re-fetches after each answer) inline
  dashboard/   api.ts, use-dashboard.ts — one endpoint, one hook, powers the whole home page
  admin/       api.ts (every /admin/* call) and skill-ref-input.tsx — the one component
               shared by all four admin CRUD pages, since every catalogue tags itself with
               the same (skill name, category) list shape
hooks/         Shared React hooks — use-require-auth.ts guards a page client-side;
               use-require-admin.ts (Phase 10) additionally bounces a non-admin to `/`
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

## Careers pages (Phase 6)

`/careers` lists every role from `GET /careers`, already ranked by score server-side — the page
just renders the order it receives. `/careers/[id]` is a client component that reads the route
param via `useParams()` (not the App Router's async `params` prop) so it can sit behind the same
`useRequireAuth()` client-side guard as every other protected page, and fetches inline with a
local `useEffect` rather than a reusable hook since it's the only place a single role's detail is
ever needed. Both pages reuse `components/ui/score-bar.tsx`, the same 0–100 score visualization
the resume analyzer uses — one shared component now that two features need identical fit-score
UI.

## Jobs & learning pages (Phase 7)

`/jobs` and `/jobs/[id]` are a straight copy of the careers pages' shape (ranked list → detail
with matched/missing skills), since job matching reuses the exact same backend scoring engine;
the job detail page adds an external "Apply" link (`target="_blank" rel="noreferrer"`) the
career pages don't need. `/learning` filters by skill via a chip row: clicking a chip re-fetches
`GET /learning-resources?skill_id=` through `use-learning-resources.ts` rather than filtering a
client-side list. The chip options themselves come from a *second*, always-unfiltered call to the
same hook — deliberately not a ref-backed cache or an effect that calls `setState`, both of which
this project's React Compiler-aware lint config forbids (see `react-hooks/refs` and
`react-hooks/set-state-in-effect`); two small requests against a ~20-resource catalogue costs
nothing. The `careers/[id]` page also calls `careerApi.getLearningPlan(id)` to render a "Close
your skill gap" section listing resources per missing skill — a best-effort fetch that fails
silently (the section just doesn't render) since it's a bonus alongside the fit score, not
required for the page to be useful.

## Interview pages (Phase 8)

`/interviews` combines a start form (optional role select, sourced from `useCareers()` — no
separate "list roles" call needed) with a list of past sessions. `/interviews/[id]` renders every
assigned question with either an inline answer form or, once answered, the submitted answer plus
its AI feedback and score. Submitting an answer calls a `refetch()` of the whole session (not a
local splice of the new answer into state) specifically so `status`, `completed_at`, and
`average_score` — which the backend may have just changed server-side (auto-completion) — stay
correct without hand-written client-side logic to mirror that transition.

## Dashboard (Phase 9)

`/` (`app/page.tsx`) replaces the Phase 2 API/DB scaffold page it started as — its own comment
said this would happen "in a later phase," and Phase 9 is it. Like every other protected page it
sits behind `useRequireAuth()`, so a logged-out visit to `/` still bounces to `/login`; login and
register now redirect to `/` instead of `/profile`.

The page is one `useDashboard()` call rendering a hero (greeting + `components/ui/progress-ring.tsx`
for profile-completion, an SVG ring sharing `ScoreBar`'s color thresholds), a `StatCard` grid
(skills count, resume score, best career match, interview average — icons from `lucide-react`,
the one new dependency this phase added), a profile checklist, a suggested-actions list, and
top-3 career/job match cards. `suggestionHref()` routes each suggestion string to the page that
addresses it via a plain substring match (`"resume"` → `/resume`, `"mock interview"` →
`/interviews`, `"career match"` → `/careers`, else `/profile`) — brittle only if the backend's
wording changes without updating this list, which is an acceptable coupling for four short rules.

## Admin panel (Phase 10)

`/admin` sits behind `hooks/use-require-admin.ts` instead of `useRequireAuth()` — it checks
`user.role === "admin"` and bounces anyone else to `/` (a logged-out visitor still goes to
`/login` first). This is UX only, same caveat as every other client-side guard in this app: the
real boundary is the backend's `require_role(UserRole.admin)` on every `/admin/*` call. The
"Admin" link in `site-header.tsx` is conditionally rendered on `user.role`, so a student never
even sees it.

The four catalogue pages (`/admin/career-roles`, `/admin/learning-resources`,
`/admin/job-postings`, `/admin/interview-questions`) all follow the same shape as the Phase 4
profile sections: a list, a `+ Add X` button that reveals an inline create form, per-item `Edit`
that swaps the same form in with values pre-filled, and `InlineConfirmButton` for delete. Unlike
the RHF + Zod forms elsewhere in the app, these are plain `useState`-controlled forms with native
`required` validation — a deliberate scope choice for internal admin tooling, matching the
similarly-plain interview-answer and resume-upload forms rather than the public-facing,
schema-validated auth/profile forms. Every form's skill field is `features/admin/
skill-ref-input.tsx`, shared across all four since every catalogue tags itself with the same
(name, category) list, added as chips with an inline text input + category select — typing a
name that doesn't exist yet in the catalogue is exactly how an admin introduces a new one.

`/admin/users` lists every account with an Activate/Deactivate toggle; the toggle for the
signed-in admin's own row is disabled client-side (title-tooltip explains why) mirroring the
backend's `400 cannot_deactivate_self` — a UX nicety, not the enforcement.
