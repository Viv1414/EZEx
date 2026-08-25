# ezpt — backlog / not-yet-built

Captured ideas that are intentionally deferred, so they don't get lost.
Nothing below is built yet.

## Exercise model — richer content
- Injury/symptom relationship: an Exercise can help with multiple Injuries,
  and each Exercise-Injury pairing has its own effectiveness rating (1-5).
  e.g. "Heel Slides" -> ankle sprain: 4/5, shin splints: 2/5.
  (Needs its own design pass -- this isn't a plain many-to-many, since the
  effectiveness rating has to live *on the pairing*, not on either side.)
- video_url — optional demonstration video
- diagram — image of the targeted body part
- equipment — list of equipment needed
- instructions — written step-by-step
- frequency — e.g. sets/reps, how often per day/week
- common_mistakes
- modifications — separate versions for beginner / intermediate / advanced

## API
- POST /exercises (create) — deferred until the model shape above is settled

## Exercise detail page (from wireframes, 2026-08-25)
- List of injuries this exercise helps with + effectiveness rating for each
  (same Injury/effectiveness relationship as above)
- "Add to program" button
- Scrollable related-exercises section at the bottom

## Programs (= "custom workouts" from the Purpose section, renamed in wireframes)
- User builds a Program by picking an injury; matching exercises surface
  ranked by effectiveness rating for that injury
- Programs can also be assigned to a client by their physiotherapist

## Dashboard (from wireframes, 2026-08-25)
- "Your Programs" row (user's active programs, plus an "add" tile)
- Search bar for finding a specific exercise directly
- "Collections" section below the fold, grouped by body part and/or injury
- Sidebar (hamburger menu) — contents not decided yet
- Profile button — implies account settings, which needs auth first

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
