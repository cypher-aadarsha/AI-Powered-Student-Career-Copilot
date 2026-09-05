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

## Structure

```
app/          Routes (App Router) — one folder per route
components/   Reusable UI (components/ui for primitives, components/layout for shells)
features/     One folder per product module (auth, profile, resume, ...), added as built
hooks/        Shared React hooks
lib/          Cross-cutting utilities — api-client.ts wraps every backend call
types/        Shared TypeScript types for API response shapes
```

`features/`, most of `components/`, and route groups beyond `/` are intentionally empty right
now — they fill in starting with the auth phase. See the design document's Frontend Folder
Structure section for the target layout.
