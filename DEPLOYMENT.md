# ezpt — deployment checklist

Not built/done yet -- a checklist for when you actually deploy. Assumes
managed platforms (e.g. Vercel for frontend, Railway/Render/Fly for
backend + a managed Postgres add-on), not a self-run VPS. If that
assumption changes, revisit this whole file.

## Environment variables to set on the platform (never commit these)
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`.
  The app **refuses to start** if `ENVIRONMENT=production` and this is
  still the code's insecure default (see core/config.py) -- that's
  intentional, don't work around it.
- `DATABASE_URL` — from whatever managed Postgres add-on you provision;
  format: `postgresql+psycopg2://user:pass@host:port/dbname`
- `CORS_ORIGINS` — your real frontend domain (e.g. `https://ezpt.app`),
  not `http://localhost:3000`
- `ENVIRONMENT=production` — flips the login cookie to `Secure` (HTTPS-only)
  and `SameSite=None` (required for the cookie to survive frontend and
  backend being on two different domains -- `lax` only works locally
  because same-domain-different-port counts as "same site"), and enables
  the SECRET_KEY startup check above
- Frontend: `NEXT_PUBLIC_API_URL` (your real backend domain) and `API_URL`
  (same value, unless frontend/backend run on the same private network)

## Must be true before real users touch this
- [ ] HTTPS is actually terminated in front of both frontend and backend
      (the login cookie's `Secure` flag requires it -- without HTTPS, the
      browser will silently refuse to send the cookie at all in production)
- [ ] `SECRET_KEY` is a freshly generated value, not reused from local dev
- [ ] Confirm the platform's reverse proxy sets `X-Forwarded-For` itself
      (overwriting any client-supplied value) rather than blindly trusting
      it -- true for Vercel/Railway/Render/Fly, but verify for whatever's
      actually chosen. core/limiter.py's rate limiting depends on this.
- [ ] Database credentials are the platform's auto-generated ones, not
      `ezpt`/`ezpt` from docker-compose.yml (that file is dev-only)

## Known gaps at launch (see ROADMAP.md for full detail)
- No email verification -- anyone can sign up with an email they don't own
- No password reset flow
- Logout doesn't revoke the JWT server-side (stays valid until its 7-day expiry)
- Rate limiting is IP-based only -- doesn't stop a slow, distributed
  brute-force against one specific account
