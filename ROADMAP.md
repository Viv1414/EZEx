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
  GET /auth/me. Backend only -- no frontend signup/login forms yet.

## Auth follow-ups (not built yet)
- "Logout" only clears the browser cookie -- the JWT itself isn't
  invalidated server-side (stateless tokens have no revocation list).
  A stolen token keeps working until it expires (currently 7 days).
  Fix later with either a short-lived token + refresh-token flow, or a
  server-side revocation list -- more machinery than a first pass needs.
- Email verification, password reset -- not built
- Frontend signup/login forms (first real Client Components in the app)

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
