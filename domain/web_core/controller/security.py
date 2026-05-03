"""
Flask Security Middleware
Protects against OWASP Top 10 vulnerabilities with comprehensive logging
"""

from ..protector import (
    CSRFProtection, InputValidator, RateLimiter
)

from ..plugin.private.security import SecurityMiddleware

from ..bootstrap import protector_logger
from flask import Flask

class Security:
    __TITLE__ = "Thunder Security"
    __VERSION__ = "1.0.0"
    __DEVELOPER__ = "LetnanGM"
    
    @staticmethod
    def setup(app: Flask) -> SecurityMiddleware:
        """
        Initialize security middleware for Flask app
        
        Usage:
            from security_middleware import setup_security
            
            app = Flask(__name__)
            app.secret_key = 'your-secret-key-here'
            security = setup_security(app)
        """
        from datetime import timedelta
        from ..utils.server.secretz import get_secret_key_server
        from ..plugin.private.security.loader import loader_security
        
        # Set secure session configuration
        app.config.update(
            SESSION_COOKIE_SECURE=True,                      # Only send cookie over HTTPS
            SESSION_COOKIE_HTTPONLY=True,                    # Prevent JavaScript access to session cookie
            SESSION_COOKIE_SAMESITE='Lax',                   # CSRF protection
            PERMANENT_SESSION_LIFETIME=timedelta(hours=1),   # Session timeout
        )
        
        app.secret_key = get_secret_key_server()
        
        # Initialize security middleware
        loader_security(app=app)
        security = SecurityMiddleware(app=app)
        
        return security

# Export main components
__all__ = [
    'SecurityMiddleware',
    'Security',
    'RateLimiter',
    'InputValidator',
    'CSRFProtection',
    'protector_logger'
]