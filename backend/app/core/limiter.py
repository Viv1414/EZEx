"""
Shared rate limiter instance. Lives in its own module (not main.py) so
routers can import it without a circular import -- main.py imports the
auth router, so the auth router can't import limiter back from main.py.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings


def get_client_ip(request: Request) -> str:
    """
    In production, every managed hosting platform (Vercel, Railway, Render,
    Fly, ...) sits a reverse proxy in front of the app -- without this,
    slowapi's default get_remote_address would see the *proxy's* IP on
    every request, collapsing the rate limit into one shared bucket for
    every visitor combined. X-Forwarded-For (set by the proxy, not the
    client) carries the real visitor's IP instead.

    Only trusted in production: locally there's no proxy, so a raw client
    could set this header themselves to fake any IP and dodge the limit --
    the direct connection (get_remote_address) is what's actually trustworthy
    there. This assumes the production proxy overwrites/sets this header
    itself rather than blindly trusting an incoming client-supplied one,
    which is true for the platforms above but isn't universal -- revisit
    if the deployment target changes to something that doesn't.
    """
    if settings.environment == "production":
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return get_remote_address(request)


# Rate-limits by client IP address. Note the scope: this stops one IP from
# hammering an endpoint, but doesn't stop a distributed attacker (many IPs)
# from slowly brute-forcing one specific account -- that's a different,
# bigger defense (e.g. per-account lockout) not built here.
limiter = Limiter(key_func=get_client_ip)
