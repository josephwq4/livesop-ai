import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("livesop_audit")

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get user from state if available (set by auth dependency)
        # Note: Middleware runs *before* dependency, so we might check response headers or process it after
        # But commonly we just log the request path/method here.
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time": f"{process_time:.4f}s",
            "client_ip": request.client.host
        }
        
        # Log to console (in production, this goes to CloudWatch/Datadog)
        logger.info(json.dumps(log_data))
        
        return response
