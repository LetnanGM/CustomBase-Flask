# inside protect.py (or wherever setup_security is defined)
from .ProtectChain import ProtectionChain


def setup_securitychain(app):
    from flask import request

    from domain.web_core.bootstrap import chainring_logger

    app = app

    """
    Initialize protection chain and register before_request hook.
    This will auto-load common protection subprotects under
    '.subprotect.*' — adjust list to suit your files.
    """
    chain = ProtectionChain()

    # list subprotects to attempt to load (adjust names to your package)
    subprotects = [
        "domain.WebController.protector.csrf.CSRF_protection",
        "domain.WebController.protector.input.InputValidator",
        "domain.WebController.protector.ratelimit.RateLimiter",
        "domain.WebController.protector.obsec.Obsecurity",
    ]

    for mod in subprotects:
        added = chain.load_from_module(mod)
        chainring_logger.debug(f"setup_security: loaded {added} handlers from {mod}")

    # fallback: if you want to always run some inline checks, add them here
    # example : chain.add(lambda req: True)

    # register global hook
    @app.before_request
    def _global_protect():
        # optionally skip static or health-check endpoints
        path = request.path or ""
        if path.startswith("/static") or path.startswith("/health"):
            return None

        # only run protections for unsafe methods; safe GETs skip
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            return chain.run(request)

    # Also add after_request to attach headers or cookies if needed (optional)
    return chain
