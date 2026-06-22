from flask import Flask, Response, abort, request

from domain.web_core.data.configuration.sys.SecurityConfig import \
    SecurityConfig


class SecurityMiddleware:
    """Main security middleware class"""

    def __init__(self, app: Flask):
        from domain.web_core.bootstrap import SMiddleware_logger
        from domain.web_core.protector import InputValidator, RateLimiter

        self.app = app
        self._log = SMiddleware_logger

        # Register middleware
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)

        self.rate_limiter = RateLimiter()
        self.validator = InputValidator()

        SMiddleware_logger.debug("Successfully Initialized 'securityMiddleware'")

    def before_request(self):
        """Process request before handling"""
        ip = request.remote_addr

        # Log request
        self._log.vsilent(
            f"Request: {request.method} {request.path} from {ip}", extra={"ip": ip}
        )

        # Check if IP is blocked
        if self.rate_limiter.is_blocked(ip):
            self._log.vsilent(f"Blocked IP attempted access: {ip}", extra={"ip": ip})
            abort(
                403,
                description="Access forbidden. Your IP has been temporarily blocked.",
            )

        # Rate limiting
        if not self.rate_limiter.check_rate_limit(ip):
            self._log.vsilent(f"Rate limit exceeded for IP: {ip}", extra={"ip": ip})
            abort(429, description="Too many requests. Please try again later.")

        # Validate all input data
        self._validate_request_data()

    def _validate_request_data(self):
        """Validate all request data"""
        ip = request.remote_addr

        # Validate form data
        if request.form:
            for key, value in request.form.items():
                if key == "csrf_token":
                    continue

                is_valid, sanitized = self.validator.validate_input(str(value))
                if not is_valid:
                    self._log.vsilent(
                        f"Malicious input detected in form field '{key}': {value[:100]}",
                        extra={"ip": ip},
                    )
                    abort(400, description="Invalid input detected")

        # Validate query parameters
        if request.args:
            for key, value in request.args.items():
                is_valid, sanitized = self.validator.validate_input(str(value))
                if not is_valid:
                    self._log.vsilent(
                        f"Malicious input detected in query parameter '{key}': {value[:100]}",
                        extra={"ip": ip},
                    )
                    abort(400, description="Invalid input detected")

        # Validate JSON data
        if request.is_json:
            try:
                json_data = request.get_json()
                self._validate_json_recursive(json_data)
            except Exception as e:
                self._log.vsilent(
                    f"Error validating JSON data: {str(e)}", extra={"ip": ip}
                )
                abort(400, description="Invalid JSON data")

    def _validate_json_recursive(self, data):
        """Recursively validate JSON data"""
        ip = request.remote_addr

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    is_valid, sanitized = self.validator.validate_input(value)
                    if not is_valid:
                        self._log.vsilent(
                            f"Malicious input detected in JSON field '{key}': {value[:100]}",
                            extra={"ip": ip},
                        )
                        abort(400, description="Invalid input detected")
                elif isinstance(value, (dict, list)):
                    self._validate_json_recursive(value)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    is_valid, sanitized = self.validator.validate_input(item)
                    if not is_valid:
                        self._log.vsilent(
                            f"Malicious input detected in JSON array: {item[:100]}",
                            extra={"ip": ip},
                        )
                        abort(400, description="Invalid input detected")
                elif isinstance(item, (dict, list)):
                    self._validate_json_recursive(item)

    def after_request(self, response: Response) -> Response:
        """Add security headers to response"""
        for header, value in SecurityConfig.SECURITY_HEADERS.items():
            response.headers[header] = value

        return response
