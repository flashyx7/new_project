from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Dict, Any, Optional
import structlog
import consul
import httpx
import os
import json
import time
from datetime import datetime, timedelta
import asyncio

# Import shared modules
import sys
import os
# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from shared.security import verify_token

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Edge Service",
    description="API Gateway and routing service",
    version="1.0.0"
)

# Security
security = HTTPBearer(auto_error=False)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
consul_port = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=consul_host, port=consul_port)

# Discovery service URL
discovery_service_url = os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:9090")

# Service routing configuration
SERVICE_ROUTES = {
    "auth-service": {
        "prefix": "/auth",
        "target_path": "/auth",
        "host": "localhost",
        "port": 8081
    },
    "registration-service": {
        "prefix": "/registration",
        "target_path": "/",
        "host": "localhost", 
        "port": 8888
    },
    "job-application-service": {
        "prefix": "/jobapplications",
        "target_path": "/",
        "host": "localhost",
        "port": 8082
    }
}

class CircuitBreaker:
    """Simple circuit breaker implementation."""

    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker reset to CLOSED")
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning("Circuit breaker opened", failure_count=self.failure_count)

            raise e

class ServiceDiscovery:
    """Service discovery and routing with circuit breaker."""

    def __init__(self):
        self.service_cache = {}
        self.circuit_breakers = {}
        self.cache_ttl = 30  # seconds

    async def get_service_instance(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service instance from discovery service with caching."""
        current_time = time.time()

        # Check cache first
        if service_name in self.service_cache:
            cache_entry = self.service_cache[service_name]
            if current_time - cache_entry["timestamp"] < self.cache_ttl:
                return cache_entry["instance"]

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{discovery_service_url}/services/{service_name}")
                if response.status_code == 200:
                    data = response.json()
                    instances = data.get("instances", [])
                    if instances:
                        instance = instances[0]
                        # Cache the result
                        self.service_cache[service_name] = {
                            "instance": instance,
                            "timestamp": current_time
                        }
                        return instance
            return None
        except Exception as e:
            logger.error("Failed to get service instance", service_name=service_name, error=str(e))
            return None

    async def route_request(self, service_name: str, path: str, method: str, 
                          headers: Dict, body: Optional[bytes] = None) -> Response:
        """Route request to appropriate service with circuit breaker."""
        # Get or create circuit breaker for this service
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()

        circuit_breaker = self.circuit_breakers[service_name]

        def make_request():
            return asyncio.create_task(self._make_request(service_name, path, method, headers, body))

        try:
            result = await circuit_breaker.call(make_request)
            return result
        except Exception as e:
            logger.error("Request routing failed", service_name=service_name, error=str(e))
            raise HTTPException(status_code=503, detail="Service unavailable")

    async def _make_request(self, service_name: str, path: str, method: str, 
                          headers: Dict, body: Optional[bytes] = None) -> Response:
        """Make the actual HTTP request to the service."""
        # Get the route configuration
        route_config = SERVICE_ROUTES.get(service_name, {})
        if not route_config:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

        target_path = route_config.get("target_path", "/")
        host = route_config.get("host", "localhost")
        port = route_config.get("port", 80)

        # Construct the target URL
        service_path = path[len(route_config['prefix']):] if path.startswith(route_config['prefix']) else path
        if not service_path.startswith('/'):
            service_path = '/' + service_path

        # Use target_path if specified, otherwise use service_path
        if target_path and target_path != "/":
            final_path = target_path + service_path
        else:
            final_path = service_path

        target_url = f"http://{host}:{port}{final_path}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=target_url,
                    headers=headers,
                    content=body
                )

                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        except httpx.TimeoutException:
            logger.error("Request timeout", service_name=service_name, url=target_url)
            raise HTTPException(status_code=504, detail="Gateway timeout")
        except httpx.ConnectError:
            logger.error("Connection error", service_name=service_name, url=target_url)
            raise HTTPException(status_code=503, detail="Service unavailable")
        except Exception as e:
            logger.error("Request failed", service_name=service_name, error=str(e))
            raise HTTPException(status_code=500, detail="Internal gateway error")

service_discovery = ServiceDiscovery()

def get_service_name_from_path(path: str) -> Optional[str]:
    """Extract service name from request path."""
    for service_name, route_config in SERVICE_ROUTES.items():
        if path.startswith(route_config["prefix"]):
            return service_name
    return None

async def route_to_service(service_name: str, path: str, method: str, 
                          headers: Dict, body: Optional[bytes] = None) -> Response:
    """Route request to appropriate service."""
    # Get the route configuration
    route_config = SERVICE_ROUTES.get(service_name, {})
    if not route_config:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    target_path = route_config.get("target_path", "/")
    host = route_config.get("host", "localhost")
    port = route_config.get("port", 80)

    # Construct the target URL
    service_path = path[len(route_config['prefix']):] if path.startswith(route_config['prefix']) else path
    if not service_path.startswith('/'):
        service_path = '/' + service_path

    # Use target_path if specified, otherwise use service_path
    if target_path and target_path != "/":
        final_path = target_path + service_path
    else:
        final_path = service_path

    target_url = f"http://{host}:{port}{final_path}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except httpx.TimeoutException:
        logger.error("Request timeout", service_name=service_name, url=target_url)
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except httpx.ConnectError:
        logger.error("Connection error", service_name=service_name, url=target_url)
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error("Request failed", service_name=service_name, error=str(e))
        raise HTTPException(status_code=500, detail="Internal gateway error")

def validate_token_dependency(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Validate JWT token if present."""
    if credentials:
        try:
            token = credentials.credentials
            token_data = verify_token(token)
            if token_data is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return token_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Token validation failed", error=str(e))
            raise HTTPException(status_code=401, detail="Authentication failed")
    return None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()

    # Log request
    logger.info("Incoming request",
               method=request.method,
               url=str(request.url),
               client_ip=request.client.host if request.client else None)

    try:
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info("Request completed",
                   method=request.method,
                   url=str(request.url),
                   status_code=response.status_code,
                   process_time=process_time)

        return response
    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error("Request failed",
                    method=request.method,
                    url=str(request.url),
                    error=str(e),
                    process_time=process_time)
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize the edge service."""
    logger.info("Edge service starting up")
    try:
        # Test Consul connection
        consul_client.agent.self()
        logger.info("Successfully connected to Consul", host=consul_host, port=consul_port)

        # Register service with discovery service
        service_registration = {
            "service_name": "edge-service",
            "service_id": "edge-service-1",
            "address": "127.0.0.1",
            "port": 8080,
            "tags": ["edge", "gateway", "routing"]
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{discovery_service_url}/register",
                json=service_registration
            )
            if response.status_code == 200:
                logger.info("Successfully registered with discovery service")
            else:
                logger.warning("Failed to register with discovery service", status_code=response.status_code)

    except Exception as e:
        logger.warning("Startup: Could not register with discovery service", error=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "edge-service", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug/{path:path}")
async def debug_path(path: str):
    """Debug endpoint to test path handling."""
    service_name = get_service_name_from_path(f"/{path}")
    return {
        "path": path,
        "full_path": f"/{path}",
        "service_name": service_name,
        "service_routes": list(SERVICE_ROUTES.keys())
    }

# Static files and templates for web interface
try:
    app.mount("/static", StaticFiles(directory="edge_service/static"), name="static")
    templates = Jinja2Templates(directory="edge_service/templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/application", response_class=HTMLResponse)
    async def application_page(request: Request):
        return templates.TemplateResponse("application.html", {"request": request})

    @app.get("/application_list", response_class=HTMLResponse)
    async def application_list_page(request: Request):
        return templates.TemplateResponse("application_list.html", {"request": request})

except Exception as e:
    logger.warning("Web interface not available", error=str(e))

    @app.get("/")
    async def fallback_index():
        return {"message": "Edge Service API Gateway", "status": "running"}

@app.api_route("/registration/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_registration(
    path: str,
    request: Request,
    token_data: Optional[Dict] = Depends(validate_token_dependency)
):
    """Route registration service requests."""
    try:
        full_path = f"/registration/{path}"
        logger.info(f"Registration request: {request.method} {full_path}")

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        # Route to registration service
        response = await route_to_service(
            service_name="registration-service",
            path=full_path,
            method=request.method,
            headers=dict(request.headers),
            body=body
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration routing failed", path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Internal gateway error")

@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_auth(
    path: str,
    request: Request,
    token_data: Optional[Dict] = Depends(validate_token_dependency)
):
    """Route auth service requests."""
    try:
        full_path = f"/auth/{path}"
        logger.info(f"Auth request: {request.method} {full_path}")

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        # Route to auth service
        response = await route_to_service(
            service_name="auth-service",
            path=full_path,
            method=request.method,
            headers=dict(request.headers),
            body=body
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Auth routing failed", path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Internal gateway error")

@app.api_route("/jobapplications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_job_applications(
    path: str,
    request: Request,
    token_data: Optional[Dict] = Depends(validate_token_dependency)
):
    """Route job application service requests."""
    try:
        full_path = f"/jobapplications/{path}"
        logger.info(f"Job application request: {request.method} {full_path}")

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        # Route to job application service
        response = await route_to_service(
            service_name="job-application-service",
            path=full_path,
            method=request.method,
            headers=dict(request.headers),
            body=body
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Job application routing failed", path=path, error=str(e))
        raise HTTPException(status_code=500, detail="Internal gateway error")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning("HTTP exception",
                  status_code=exc.status_code,
                  detail=exc.detail,
                  path=str(request.url))

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception",
                error=str(exc),
                path=str(request.url))

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)