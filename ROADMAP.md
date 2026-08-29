# ezpt — backlog / not-yet-built

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

## Known issues (deprioritized, 2026-08-28)
- Login page: clicking "Log in" while an error is already showing causes
  the button to visibly glitch. Not investigated yet.

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
- Email verification, password reset -- not built
- ✅ Frontend signup/login forms (first real Client Components in the app)
- ✅ Site gated behind login (frontend/middleware.ts): "/" is now a public
  placeholder landing page, everything else (including /dashboard) redirects
  there if the access_token cookie is missing.
- ✅ Backend API itself now requires login too (all 5 GET /exercises*,
  /injuries* endpoints have Depends(get_current_user)) -- no longer
  bypassable via curl/Postman. Server Components forward the browser's
  cookie manually via lib/server-auth.ts's getAuthCookieHeader()
  (next/headers' cookies()), passed into each lib/api.ts call.
- ⚠️ Still true: the middleware gate itself only checks cookie *presence*,
  not signature/expiry -- an expired-but-present cookie gets past
  middleware, then the actual data fetch 401s and the page throws an
  unhandled error instead of a clean redirect to /login. Minor, not fixed yet.

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

## 🔴 CSRF -- must build before Programs (or any other mutating endpoint), not after
Fixing the cookie's SameSite for split-domain deployment (above) was necessary
but has a side effect: `SameSite=lax` incidentally blocked cross-site form
submissions/fetches, which is also what stops classic CSRF. `SameSite=none`
(required once frontend/backend are on different domains) removes that
protection. CORS does NOT cover this gap -- CORS only governs whether
cross-origin JavaScript can *read a response*, not whether a plain HTML
form can be submitted cross-site with cookies attached.
- Low impact today: only /auth/login (login-CSRF) and /auth/logout exist
  to target, neither very damaging.
- High impact once Programs exist: a malicious page could silently
  create/edit/delete a logged-in victim's program.
- Fix: a CSRF token (e.g. double-submit cookie pattern, or a custom header
  the backend requires on state-changing requests) checked on every
  POST/PUT/DELETE. Build this alongside Programs' first mutating endpoint,
  not as an afterthought once mutations already exist.
  (components/Header.tsx, replaces the old AuthStatus.tsx).

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
- User builds a Program by picking an injury; matching exercises surface
  ranked by effectiveness rating for that injury
- Programs can also be assigned to a client by their physiotherapist

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
