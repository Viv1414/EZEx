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

## Physiotherapist features (after core site is built)
- Physiotherapist sign-in / role
- Build & assign workouts to clients
- Upload their own exercises

## Already tracked elsewhere
- Auth, env separation, rate limiting on AI features, ToS/liability — see CLAUDE.md
