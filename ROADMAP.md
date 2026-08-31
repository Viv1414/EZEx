# ezex — backlog / not-yet-built

Captured ideas that are intentionally deferred, so they don't get lost.
Items are ✅ once built; everything else below is still not built.

## Done (technical summary)
- Injury/symptom relationship (Exercise <-> Injury, effectiveness 1-5 per pairing)
- GET /exercises, /exercises/{id}, /exercises/general-parts, /injuries, /injuries/{id}/exercises
- Search (`GET /exercises?q=`): matches name, body_part, general_part, and linked injury names
- Collections by general_part + by injury, exercise detail page, homepage
- Exercise content fields: video_url, diagram_url, frequency, equipment,
  instructions, common_mistakes, modification_beginner/intermediate/advanced
  (`description` removed from the model -- instructions supersede it)
- Auth: POST /auth/signup, /auth/login (httpOnly JWT cookie), /auth/logout,
  GET /auth/me, plus frontend /signup and /login forms + header AuthStatus.
- ✅ Programs (2026-08-31): Program + ProgramExercise (join table, same
  many-to-many reasoning as ExerciseInjury -- one Program has many
  Exercises, one Exercise can sit in many different users' Programs).
  Backend: POST/GET /programs, GET/DELETE /programs/{id},
  POST /programs/{id}/exercises, DELETE /programs/{id}/exercises/{exercise_id}
  -- all mutating ones require Depends(require_csrf) (first real use of
  the CSRF infra built just before this). Every endpoint checks ownership
  (get_owned_program returns None for "doesn't exist" and "isn't yours"
  alike -> both surface as 404, so a stranger can't even confirm an ID
  exists) -- this is the first model in the app where per-user ownership
  matters at all. Creating from an injury bulk-adds that injury's
  exercises ranked by effectiveness (verified: shin splints -> Heel
  Slides then Ankle Alphabet, matching known ratings). Frontend:
  dashboard "Your Programs" section, /programs/new, /programs/[id]
  (ProgramDetailView.tsx handles remove-exercise/delete-program),
  "Add to program" button on the exercise page. Verified end to end
  through the real pages, not just the API.
- ⚠️ Minor, low priority: User has no cascade delete toward
  EmailVerificationToken or Program (hit the FK violation manually
  cleaning up test accounts three times now). Only matters once an actual
  "delete my account" feature exists (not built/planned yet) or for
  manual dev cleanup -- not worth a migration just for that today.


## Auth follow-ups (not built yet)
- ✅ Logout now actually revokes the specific token server-side (jti +
  revoked_tokens table, checked in get_current_user) -- verified: the exact
  same JWT that worked pre-logout returns 401 post-logout, even though it
  hasn't naturally expired. A fresh login for the same user is unaffected
  (only that one token is revoked, not all of a user's sessions).
  Token lifetime also shortened from 7 days to 1 day.
  Chose this over a full refresh-token flow (the other standard fix) since
  it fully solves logout for realistic effort; refresh tokens additionally
  protect a token that's stolen but never logged out of (shorter natural
  lifetime) -- worth revisiting if that scenario becomes a real concern.
- ✅ Email verification (2026-08-30): User.is_verified + EmailVerificationToken
  (single-use, 24h expiry). Signup sends a real email via Mailpit (new
  docker-compose service, local dev only -- swap SMTP_* env vars for a real
  provider at deploy time, no code change, see core/email.py). Unverified
  users can log in but get 403 from every data endpoint
  (get_current_verified_user), and the frontend (lib/api.ts's
  redirectIfUnverified) bounces them to /verify, which has a
  resend button (POST /auth/resend-verification). /verify-email reads the
  emailed token and completes verification. Verified end to end through
  Mailpit's real inbox, not just the API.
  ⚠️ Pre-existing accounts (created before this feature) are now
  is_verified=false and will be blocked until they verify or someone
  flips that column manually -- includes the vivaan@example.com test
  account used earlier in this session.
- Password reset -- not built
- ✅ Frontend signup/login forms (first real Client Components in the app)
- ✅ Site gated behind login (frontend/middleware.ts): "/" is now a public
  placeholder landing page, everything else (including /dashboard) redirects
  there if the access_token cookie is missing.
- ✅ Backend API itself now requires login too (all 5 GET /exercises*,
  /injuries* endpoints have Depends(get_current_user)) -- no longer
  bypassable via curl/Postman. Server Components forward the browser's
  cookie manually via lib/server-auth.ts's getAuthCookieHeader()
  (next/headers' cookies()), passed into each lib/api.ts call.
- ✅ The middleware gate still only checks cookie *presence*, not
  signature/expiry, but the gap is closed: lib/api.ts's
  redirectOnAuthError (generalized from redirectIfUnverified) now
  redirects a 401 to /login instead of letting the page crash. Verified
  with a tampered cookie that passes middleware but fails backend
  validation -- now redirects cleanly.
- Login page: clicking "Log in" while an error is already showing caused
  a brief button glitch -- fixed (per user, cause/fix not detailed here).

## Security hardening (2026-08-28)
- ✅ SECRET_KEY: app now refuses to start if ENVIRONMENT=production and
  SECRET_KEY is still the code's insecure default (core/config.py). Local
  .env given a real generated secret instead of that default too.
- ✅ Rate limiting (slowapi): /auth/login and /auth/signup limited to
  5/minute per IP -- stops naive scripted brute-forcing/mass-signup.
  IP detection (core/limiter.py) trusts X-Forwarded-For only in production
  (assumes the hosting platform's proxy sets it itself, not a raw client).
- ✅ Cookie SameSite fixed for split-domain deployment: "none" (+ Secure)
  in production, "lax" locally -- see DEPLOYMENT.md for why "lax" would
  have silently broken auth once frontend/backend are on different domains.
- ✅ DEPLOYMENT.md created -- checklist for env vars, HTTPS, DB credentials,
  and known gaps to revisit before real users arrive.
- Header logo now goes to /dashboard when logged in, "/" when logged out
  (components/Header.tsx, replaces the old AuthStatus.tsx).

## ✅ CSRF (2026-08-30)
Token is derived, not stored: `HMAC(secret_key, jti)` (core/security.py's
create_csrf_token/verify_csrf_token) -- tied to the session's jti, so it
naturally becomes invalid the moment that session is revoked, no extra
bookkeeping needed. Handed to the frontend in the login/me response body
(not a second cookie -- frontend and backend are different domains, so JS
on the frontend can't read a cookie the backend set anyway). Frontend
holds it in memory (lib/api.ts's module-level csrfToken, refreshed by
login()/getCurrentUser()) and sends it as `X-CSRF-Token` on mutating
requests. core/deps.py's require_csrf checks it; wired up to
POST /auth/logout as the first protected endpoint -- verified: missing
or wrong header -> 403, correct header -> succeeds and still revokes the
session correctly. Any future mutating endpoint (Programs, etc.) adds
`Depends(require_csrf)` alongside `Depends(get_current_user)`.
Login itself stays unprotected on purpose -- there's no session/jti yet
at that moment to derive a token from, and the impact (forcing a login)
is low.

## Data integrity (not enforced yet)
- Every exercise should have >=1 linked injury -- otherwise there's no way
  to surface it (an exercise is only reachable via search or a collection/
  injury browse page right now). Not a bug today since only seed.py creates
  exercises and it always links injuries -- becomes a real concern once
  POST /exercises exists. Add validation then (reject create/update if the
  injuries list is empty), rather than a DB constraint (hard to express
  "must have >=1 related row" in plain SQL without a trigger).

## Exercise model — richer content
- ✅ Injury/symptom relationship: an Exercise can help with multiple Injuries,
  and each Exercise-Injury pairing has its own effectiveness rating (1-5).
  e.g. "Heel Slides" -> ankle sprain: 4/5, shin splints: 2/5.
  (Needs its own design pass -- this isn't a plain many-to-many, since the
  effectiveness rating has to live *on the pairing*, not on either side.)
- ✅ video_url — optional demonstration video
- ✅ diagram — image of the targeted body part
- ✅ equipment — list of equipment needed
- ✅ instructions — written step-by-step
- ✅ frequency — e.g. sets/reps, how often per day/week
- ✅ common_mistakes
- ✅ modifications — separate versions for beginner / intermediate / advanced

## API
- POST /exercises (create) — deferred until the model shape above is settled

## Exercise detail page (from wireframes, 2026-08-25)
- ✅ List of injuries this exercise helps with + effectiveness rating for each
  (same Injury/effectiveness relationship as above)
- "Add to program" button
- Scrollable related-exercises section at the bottom

## Programs (= "custom workouts" from the Purpose section, renamed in wireframes)
- ✅ User builds a Program by picking an injury; matching exercises surface
  ranked by effectiveness rating for that injury (see Done section above)
- Programs can also be assigned to a client by their physiotherapist --
  still deferred, needs the PT role system (see Physiotherapist features)

## Dashboard (from wireframes, 2026-08-25)
- "Your Programs" row (user's active programs, plus an "add" tile)
- ✅ Search bar for finding a specific exercise directly
- ✅ "Collections" section below the fold, grouped by body part and/or injury
- Sidebar (hamburger menu) — contents not decided yet
- Profile button — implies account settings; backend auth now exists,
  but there's no frontend signup/login/profile UI yet

## AI symptom-input chatbot
- Wrapper around an open-source model, brief structured line of questioning
- ⚠️ Wireframe notes described this as giving the user "an advised diagnosis."
  Per the Purpose/liability section of CLAUDE.md, this needs to be reframed
  before build: suggests a *likely injury type* based on stated symptoms,
  explicitly not a diagnosis, with a persistent disclaimer near the feature.
- Needs rate limiting (per CLAUDE.md)

## Physiotherapist features (after core site is built)
- Physiotherapist sign-in / role
- Build & assign workouts (Programs) to clients
- Upload their own exercises

## Already tracked elsewhere
- Auth, env separation, rate limiting on AI features, ToS/liability — see CLAUDE.md
