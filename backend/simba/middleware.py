import logging

from decouple import config

from core.services import logToSlack
import uuid


class SlackErrorHandler(logging.Handler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def emit(self, record):
		try:
			log_entry = self.format(record)
			logToSlack(
				config("ERROR_LOGS_SLACK_URL"),
				{
					"text": f":warning: *DJANGO ERROR ALERT*\n*Logger name*: {record.name}\n*Logged message*: {log_entry}",
				},
			)

		except Exception:
			self.handleError()


# enables security features like HTTPS Redirect, HSTS, defines CSP
class SecurityHeadersMiddleware:
	"""
	Middleware to add robust security headers to all responses
	"""

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)

		# Basic protections
		response["X-Content-Type-Options"] = "nosniff"
		response["X-Frame-Options"] = "DENY"
		response["X-XSS-Protection"] = "1; mode=block"
		response["Referrer-Policy"] = "strict-origin-when-cross-origin"

		# Permissions Policy (formerly Feature Policy)
		response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"

		# Content Security Policy (CSP)
		csp_policy = (
			"default-src 'self'; "
			"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
			"style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
			"font-src 'self' https://fonts.gstatic.com data:; "
			"img-src 'self' data: https: blob:; "
			"connect-src 'self' https://api.smartcomply.com wss: ws:; "
			"frame-ancestors 'none'; "
			"base-uri 'self'; "
			"object-src 'none';"
		)
		response["Content-Security-Policy"] = csp_policy

		return response


class RequestLoggingMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)

		# Only log POST requests for activity tracking
		# if request.method == "POST" and request.path.startswith("/payments/"):
		#     user = getattr(request, "user", None)
		#     username = user.username if user and user.is_authenticated else "Anonymous"
		#     logging.getLogger(__name__).info(
		#         f"Activity: {request.path} | User={username} initiated payment"
		#     )

		return response

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # get request id from headers if provided
        request_id = request.headers.get('X-Request-ID')
        
        # else create request ID UUID
        if not request_id:
            request_id = str(uuid.uuid4())
            
        request.request_id = request_id
        
        response = self.get_response(request)
        
        # add request id to response header
        response['X-Request-ID'] = request_id
        
        return response