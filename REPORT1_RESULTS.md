# Code Review #1 — Programs + Password Reset

Multi-angle review (`/code-review high`) of `git diff HEAD~2...HEAD` (Programs
CRUD + password reset + program name length limit), run 2026-08-31/09-01.
8 independent review passes (correctness, removed-behavior, cross-file
tracing, duplication, simplification, efficiency, architecture, and
CLAUDE.md-conventions compliance). Nothing catastrophic found — no exposed
secrets, no auth bypass, no data leak. Below is every finding, prioritized.

Status legend: ⬜ not fixed yet. Update to ✅ as items are addressed.

## Should fix before relying on this in front of real users

⬜ **1. Missing health disclaimer on the Program-building feature**
`frontend/components/NewProgramForm.tsx` (lines ~52-70) — the "Build from an
injury" dropdown auto-adds every exercise ranked for that injury, most
effective first (confirmed in `backend/app/services/program_service.py`'s
`create_program`). This is exactly the kind of injury/symptom-based
suggestion feature CLAUDE.md requires a disclaimer near ("This is not a
diagnosis. Always consult a licensed physiotherapist."). Grepped the whole
frontend for "diagnosis|physiotherapist|disclaimer|Always consult" — zero
matches anywhere. No disclaimer exists near this feature at all.

⬜ **2. Deploy-day mass logout bug**
`backend/app/core/security.py` (`create_access_token`/`decode_access_token`,
~lines 38-64) — the new `iat` claim is required, and `decode_access_token`
does `payload["iat"]` unconditionally. Any token issued *before* this ships
lacks that field, raises `KeyError`, and gets treated as "invalid or expired
session" (401) via the existing broad exception catch. Since tokens live 1
day (`access_token_expire_minutes`, config.py), every user with a session
from roughly the prior 24 hours gets silently logged out the moment this
deploys — indistinguishable from a bug/attack to them. Fix: treat a missing
`iat` as "issued at the epoch" (or otherwise not present) rather than
failing to decode, so old tokens degrade gracefully instead of erroring.

✅ **3. `POST /programs` with a bad `injury_id` crashes with a raw 500** -- FIXED: injury_service.get_injury() existence check added to the router before calling create_program, mirroring add_exercise's pattern. Verified: bad injury_id now returns a clean 404.
`backend/app/services/program_service.py` (`create_program`, lines ~9-23).
No existence check on `injury_id` before `Program(...)` + `db.flush()`/
`db.commit()`. `injury_service.get_exercises_for_injury` silently returns
`[]` for a nonexistent injury (doesn't error), so nothing catches the bad ID
until Postgres's FK constraint rejects the insert with an unhandled
`IntegrityError` → 500. `add_exercise` already validates its `exercise_id`
this same way (`exercise_service.get_exercise(...)` before insert) —
`create_program` should do the equivalent for `injury_id`.

✅ **4. Reset-password token consumed before the password hash succeeds** -- FIXED two ways: (a) passwords restricted to printable ASCII (`schemas/validators.py`'s `validate_ascii_printable_charset`, shared with program names) plus `MAX_PASSWORD_LENGTH` set to exactly 72 -- since ASCII is always 1 byte/char, this exactly matches bcrypt's 72-*byte* limit with no possibility of exceeding it, and needs no separate byte-length check or "your password used too many bytes" message (superseded an earlier attempt that instead lowered the max to 18 assuming worst-case 4-byte characters -- this is strictly better, more generous, since the character set itself is now the guarantee); (b) `reset_password()` reordered to hash first, consume the token only after the hash succeeds, as defense in depth for any other hash failure. Verified via a properly UTF-8-encoded emoji payload (not typed directly in a shell command, which mangles multi-byte characters) that both signup and reset-password correctly reject non-ASCII passwords with a clean 422.
`backend/app/services/password_reset_service.py` (`reset_password`, lines
~48-63). The token row is deleted and committed *before* `hash_password`
runs. `ResetPasswordRequest.new_password` only checks character count
(8-30), but bcrypt rejects inputs over 72 *bytes* — a 30-character password
built from multi-byte characters (e.g. emoji) can exceed that and raise
`ValueError`. By then the single-use token is already gone: the request
500s, the password never changes, and the user's only reset link is
permanently spent. Fix: hash the new password first, and only delete/commit
the token once the password update has actually succeeded.

✅ **5. Race condition on "Add to program" (TOCTOU)** -- FIXED: program_service.add_exercise() now catches the IntegrityError from the DB unique constraint and returns None instead of crashing; router converts that into a clean 409. Verified with two genuinely concurrent requests: one 200, one 409, no 500.
`backend/app/routers/programs.py` (`add_exercise`, ~lines 54-63) +
`backend/app/services/program_service.py` (`add_exercise`, ~lines 37-43).
The "already in this program" check and the insert aren't atomic. Two
near-simultaneous requests (double-click, two tabs) can both pass the check
before either commits; the second commit then violates the
`uq_program_exercise` unique constraint and raises an unhandled
`IntegrityError` → 500, instead of the intended clean 409.

✅ **6. `PasswordResetToken` has the same missing-cascade-delete gap already
flagged (and accepted) for two other tables** -- FIXED properly instead of
just documented: added `ondelete="CASCADE"` at the actual DB level (not
just an ORM-side `cascade=`, which wouldn't fire for raw SQL deletes) on
all 4 affected FKs -- `email_verification_tokens.user_id`,
`password_reset_tokens.user_id`, `programs.user_id`, and
`program_exercises.program_id` (needed so the cascade can continue one
level past `programs` once a user is deleted). Verified: deleting a user
in a single `DELETE FROM users` statement, with an existing verification
token + program + program-exercise rows all still attached, now leaves
zero orphaned rows anywhere.
`backend/app/models/password_reset_token.py` — same `user_id` FK, no
cascade, as the already-noted `EmailVerificationToken`/`Program` gap in
ROADMAP.md. Wasn't caught when this table was added alongside that very
note. Not urgent (same reasoning as the other two — only matters for
account deletion, which doesn't exist yet, or manual dev cleanup) but should
be folded into that same ROADMAP item so it isn't missed a third time.

✅ **7. Whitespace-only program name passes server-side validation** -- FIXED
alongside #4: `schemas/validators.py`'s `validate_not_blank` strips and
rejects an all-whitespace name (`{"name": "    "}` -> clean 422 "Program
name cannot be blank"), and also trims incidental leading/trailing
whitespace on otherwise-valid names (`"  Leg Day  "` -> stored as
`"Leg Day"`). Also added the matching ASCII-only charset restriction to
`ProgramCreate.name` (user independently added this client-side first;
this closes the same client/server gap as #4, just for program names).
`backend/app/schemas/program.py` (`ProgramCreate.name`, line ~11) — only
checked character count (4-25), not blank/whitespace content. The frontend's
`.trim()` check in `NewProgramForm.tsx` prevents this through the UI, but a
direct `POST /programs {"name": "    "}` created a program with a blank
display name.

⬜ **8. Latent timing edge case: `iat` truncation vs. `password_changed_at` precision**
`backend/app/core/security.py` (JWT `iat`, whole-seconds precision) vs.
`backend/app/core/deps.py` (`issued_at < password_changed_at` comparison,
`password_changed_at` stored with microsecond precision). A token issued in
the same UTC second as a password reset could have its floored `iat` compare
as earlier than the reset timestamp, wrongly rejecting a session that was
actually created after the reset. Low real-world likelihood today (the
reset flow doesn't auto-login — see `reset-password/page.tsx`), but a real
edge case for any fast scripted client or future "log in immediately after
reset" UX.

## Real, but not urgent (performance at current scale)

⬜ **9. N+1 queries loading a program's exercises**
`backend/app/routers/programs.py` (`_to_detail`, lines ~13-24) — no
`selectinload`/`joinedload` on `Program.exercise_links` or
`ProgramExercise.exercise`, so `GET /programs/{id}` issues 1 + 1 + N
queries for a program with N exercises. Compounds further because
`add_exercise`/`remove_exercise` call `db.refresh(program)` right before
`_to_detail`, re-triggering the whole chain on every single add/remove.

⬜ **10. `add_exercise` loads the entire relationship just to count rows**
`backend/app/services/program_service.py` (`add_exercise`, line ~38) —
`len(program.exercise_links)` to compute the next `order_index` forces a
full lazy-load of every row. A `SELECT COUNT(*)` or DB-computed default
would be a single scalar round trip regardless of program size.

⬜ **11. Redundant `db.refresh()` calls that are no-ops**
`backend/app/routers/programs.py` (~lines 60-69, 72-81) and
`backend/app/services/program_service.py` (`add_exercise`, ~lines 35-39) —
`SessionLocal` defaults to `expire_on_commit=True`, so the explicit
`db.refresh(program)`/`db.refresh(link)` calls after `db.commit()` are
mostly redundant with what SQLAlchemy would already do lazily on next
access; `db.refresh(link)` specifically refreshes a value that's discarded
immediately (the router rebuilds its response from `program`, not `link`).

## Code-quality / architecture feedback (not bugs)

⬜ **12. `password_reset_service.py` and `email_verification_service.py` are
near-duplicate** (same for their models `PasswordResetToken` /
`EmailVerificationToken`) — identical "single-use expiring emailed token"
shape implemented twice. Worth factoring into one shared mechanism
(parameterized by purpose) before a third similar feature (e.g. a PT-invite
flow) copies the pattern a third time.

⬜ **13. Ownership-check pattern (`_get_owned_or_404`) is Program-specific,
not a reusable primitive** — ROADMAP already lists PT-assigned programs and
uploaded exercises as next, both of which need the same "does this belong
to the caller" gate. Worth extracting into `app/core/` before it's
re-derived by hand a second/third time (and the "never leak existence via
403" detail forgotten somewhere).

⬜ **14. Two independent, differently-shaped session-invalidation mechanisms**
sit side by side in `get_current_user` — per-token revocation (jti lookup
table, for logout) and per-user timestamp cutoff (`password_changed_at`,
for password reset). No shared "is this session still valid" abstraction to
extend for the next bulk-invalidation need (e.g. a future "log out of all
other devices" button).

⬜ **15. Five frontend files hand-roll the same async-state pattern** —
`AddToProgramButton.tsx`, `NewProgramForm.tsx`, `ProgramDetailView.tsx`,
`forgot-password/page.tsx`, `reset-password/page.tsx` each redefine their
own pending-flag + error-state + try/catch shape (with 3 different naming
conventions: `status`, `submitting`, `busy`). Same for repeated literal
Tailwind class strings across the same files. A shared hook/component would
prevent behavior and styling drifting apart across pages over time.

⬜ **16. `isValidPasswordLength`/`isValidProgramName` in `validation.ts` are
structurally identical** aside from which constants they close over —
could be one generic `isValidLength(value, min, max)`.

⬜ **17. Manual dict-building in `_to_detail` (and the same pattern already
in `injuries.py`/`exercises.py`) re-implements what Pydantic schemas could
do via field aliasing** — `{**Schema.model_validate(x).model_dump(), "extra": ...}`
appears 3 times independently instead of one shared helper.

⬜ **18. Validation constants (password length, program name length)
duplicated frontend/backend with no single source of truth** — same values
hand-copied in `backend/app/schemas/*.py` and `frontend/lib/validation.ts`;
easy to drift if either side changes without remembering the other.
