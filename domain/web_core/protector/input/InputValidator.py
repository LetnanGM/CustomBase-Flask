from flask import request
import bleach
import html
import re

from ...bootstrap import (SecurityConfig, iv_logger)

class detector:
    def __init__(self, data: str) -> None:
        self._data = data
        
    def detect_sql_injection(self) -> bool:
        """Detect SQL injection attempts"""
        data_lower = self._data.lower()
        for pattern in SecurityConfig.SQL_INJECTION_PATTERNS:
            if re.search(pattern, data_lower, re.IGNORECASE):
                return True
        return False
    
    def detect_xss(self) -> bool:
        """Detect XSS attempts"""
        for pattern in SecurityConfig.XSS_PATTERNS:
            if re.search(pattern, self._data, re.IGNORECASE):
                return True
        return False
    
    def detect_path_traversal(self) -> bool:
        """Detect path traversal attempts"""
        for pattern in SecurityConfig.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, self._data, re.IGNORECASE):
                return True
        return False
    
    def detect_command_injection(self) -> bool:
        """Detect command injection attempts"""
        for pattern in SecurityConfig.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, self._data):
                return True
            
        return False
    
class InputValidator:
    """Validates and sanitizes user input"""
    def __init__(self) -> None:
        self._detect = detector
    
    def _scan(self, data: str):
        detect = self._detect(data)
        
        # Check for various injection attempts
        if detect.detect_sql_injection(data):
            iv_logger.vsilent(
                f"SQL Injection attempt detected: {data[:100]}",
                extra={'ip': request.remote_addr}
            )
            return False, ""
        
        if detect.detect_xss(data):
            iv_logger.vsilent(
                f"XSS attempt detected: {data[:100]}",
                extra={'ip': request.remote_addr}
            )
            return False, ""
        
        if detect.detect_path_traversal(data):
            iv_logger.vsilent(
                f"Path traversal attempt detected: {data[:100]}",
                extra={'ip': request.remote_addr}
            )
            return False, ""
        
        if detect.detect_command_injection(data):
            iv_logger.vsilent(
                f"Command injection attempt detected: {data[:100]}",
                extra={'ip': request.remote_addr}
            )
            return False, ""
        
        return True
    
    @staticmethod
    def sanitize_input(data: str) -> str:
        """Sanitize user input"""
        # HTML escape
        data = html.escape(data)
        
        # Remove potentially dangerous characters
        data = bleach.clean(data, tags=[], strip=True)
        
        return data
    
    @staticmethod
    def validate_input(data: str, input_type: str = "text") -> tuple[bool, str]:
        """
        Comprehensive input validation
        Returns: (is_valid, sanitized_data)
        """
        if not data:
            return True, ""
        
        InputValidator()._scan(data)
        
        # Sanitize input
        sanitized = InputValidator.sanitize_input(data)
    
        return True, sanitized

