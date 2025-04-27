# Built-Ins
from typing import Dict
from time import time
from collections import defaultdict

# Installeds
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.ip_request_counts: Dict[str, float] = defaultdict(float)

    async def dispatch(self, request: Request, call_next):
        # If client is opening /app openapi schema swagger endpoint then there is no need for rate limit check  
        if request.url.path.startswith("/app"):
            return await call_next(request)
    
        # Extracting requesting client's ip 
        client_ip = request.client.host
        current_time = time()

        # Checking if there is already a request from the same ip within same second
        if current_time - self.ip_request_counts[client_ip] < 1 :
            return JSONResponse({
                "message": "Rate limit exceeded"
            }, status_code=429)
        
        # If not, updating the ip request count into dictionary 
        self.ip_request_counts[client_ip] = current_time

        # Completing the request
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time

        # Adding a custom header for the response time without changing anything in default headers
        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header,value)

        # Sending back the response to the requesting client
        return response