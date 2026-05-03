import hmac
import hashlib
import secrets
from .model import CSRFConf
from typing import Tuple

class CSRFToken:
    def __init__(self):
        self._pattern = {"cookie": "csrf_token"}
        
    def token(self, length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    @property
    def register_to_session(self) -> str:
        from flask import session
        
        token = self.token()
        if self._pattern["cookie"] not in session:
            session[self._pattern["cookie"]] = token
            
        return token
    
    @property
    def raw(self) -> str:
        return self.token()

class BuildToken:
    def __init__(self) -> None:
        self._token = None
        self._signature = None
    
    @property
    def combine_token(self) -> bytes | str:
        """
        combine token with signatures
        """
        combined_token = f"{self._token}.{self._signature}"
        return combined_token
    
    @property
    def TokenPlace(self) -> CSRFToken:
        """Generate a new CSRF token (backward compatibility)"""
        return CSRFToken()
    
    
    def generate_token_with_binding(self, secret_key: str, ip: str, user_agent: str) -> Tuple[str, CSRFToken]:
        """
        Generate CSRF Token with IP and UA (User-Agent) binding.
        
        In the future: will use timestamp, fingerprint, 
        """
        base_token = secrets.token_urlsafe(CSRFConf.BASE_TOKEN_NUMBER)
        
        binding_data = f"{ip}:{user_agent}:{base_token}"
        secretz_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        
        signature = hmac.new(
            key=secretz_key, 
            msg=binding_data.encode(), 
            digestmod=hashlib.sha256
        ).hexdigest()[:16]
        
        self._token = base_token
        self._signature = signature
        
        return self.combine_token, CSRFToken()