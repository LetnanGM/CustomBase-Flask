import hashlib
import hmac
from datetime import datetime

from flask import request, session

from .generator import BuildToken
from .model import CSRFLogger, TokenMetadata, _PrivModel


class CSRFHelper(_PrivModel):
    def __init__(self, app_instance) -> None:
        self.secret_key = app_instance.secret_key

        self._gen = BuildToken()

    def _generate_token_with_binding(self, ip: str, user_agent: str) -> str:
        """
        Generate CSRF token with IP and UA binding.

        """
        combined_token, CSRFToken = self._gen.generate_token_with_binding(
            secret_key=self.secret_key, ip=ip, user_agent=user_agent
        )

        CSRFToken.register_to_session

        # Store metadata
        self.token_metadata[combined_token] = TokenMetadata(
            token=combined_token,
            created_at=datetime.now(),
            ip=ip,
            user_agent=user_agent,
        )

        return combined_token

    def generate_smart_token(self) -> str:
        """Generate smart CSRF token with binding"""
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent", "")

        # Check if current token needs rotation
        current_token = session.get("csrf_token")
        if current_token and not self._should_rotate_token(current_token):
            return current_token

        # Generate new token with binding
        new_token = self._generate_token_with_binding(ip, user_agent)
        session["csrf_token"] = new_token

        CSRFLogger.vsilent(
            f"🔐 New CSRF token generated for IP: {ip}",
            extra={"ip": ip, "token": new_token[:16] + "..."},
        )

        return new_token

    def _verify_token_binding(self, token: str, ip: str, user_agent: str) -> bool:
        """Verify token binding to IP and UA"""
        if "." not in token:
            return False

        base_token, provided_signature = token.rsplit(".", 1)

        # Recreate signature
        binding_data = f"{ip}|{user_agent}|{base_token}"
        expected_signature = hmac.new(
            (
                self.secret_key.encode()
                if isinstance(self.secret_key, str)
                else self.secret_key
            ),
            binding_data.encode(),
            hashlib.sha256,
        ).hexdigest()[:16]

        return hmac.compare_digest(expected_signature, provided_signature)

    def _should_rotate_token(self, token: str) -> bool:
        """Decide if token should be rotated"""
        from .validate import Validate

        validator = Validate()

        if token not in self.token_metadata:
            return True

        metadata = self.token_metadata[token]

        # Rotate if expired
        if validator._is_token_expired(token):
            return True

        # Rotate if used many times
        if metadata.usage_count > 20:
            return True

        # Rotate if compromised
        if metadata.is_compromised:
            return True

        return False

    def get_csrf_token(self) -> tuple:
        method = {
            "headers": lambda: request.headers["X-CSRF-Token"],
            "form": lambda: request.form["csrf_token"],
            "json_body": lambda: request.json["csrf_token"],
            "cookie": lambda: request.cookies.get("csrf_token"),
        }

        for name, func in method.items():
            token = func()
            if token:
                return name, token
