from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Dict, Any, Optional
import structlog
import consul
import httpx
import os
import json

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
        "target_path": "/auth"
    },
    "registration-service": {
        "prefix": "/registration",
        "target_path": "/"
    },
    "job-application-service": {
        "prefix": "/jobapplications",
        "target_path": "/"
    }
}

class ServiceDiscovery:
    """Service discovery and routing."""
    
    def __init__(self):
        self.service_cache = {}
    
    async def get_service_instance(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get service instance from discovery service."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{discovery_service_url}/services/{service_name}")
                if response.status_code == 200:
                    data = response.json()
                    instances = data.get("instances", [])
                    if instances:
                        # Return the first available instance
                        return instances[0]
            return None
        except Exception as e:
            logger.error("Failed to get service instance", service_name=service_name, error=str(e))
            return None
    
    async def route_request(self, service_name: str, path: str, method: str, 
                          headers: Dict, body: Optional[bytes] = None) -> Response:
        """Route request to appropriate service."""
        instance = await self.get_service_instance(service_name)
        if not instance:
            raise HTTPException(status_code=503, detail=f"Service {service_name} not available")
        
        # Get the route configuration
        route_config = SERVICE_ROUTES.get(service_name, {})
        target_path = route_config.get("target_path", "/")
        
        # Construct the target URL
        # Remove the prefix from the path to get the service-specific path
        service_path = path[len(route_config['prefix']):] if path.startswith(route_config['prefix']) else path
        # Ensure the path starts with /
        if not service_path.startswith('/'):
            service_path = '/' + service_path
        target_url = f"http://{instance['address']}:{instance['port']}{service_path}"
        
        try:
            async with httpx.AsyncClient() as client:
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
        except Exception as e:
            logger.error("Failed to route request", service_name=service_name, error=str(e))
            raise HTTPException(status_code=503, detail="Service unavailable")

service_discovery = ServiceDiscovery()

def get_service_name_from_path(path: str) -> Optional[str]:
    """Extract service name from request path."""
    for service_name, route_config in SERVICE_ROUTES.items():
        if path.startswith(route_config["prefix"]):
            return service_name
    return None

def validate_token_dependency(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Validate JWT token if present."""
    if credentials:
        token = credentials.credentials
        token_data = verify_token(token)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return token_data
    return None

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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{discovery_service_url}/register",
                json=service_registration
            )
            if response.status_code == 200:
                logger.info("Successfully registered with discovery service")
            else:
                logger.warning("Failed to register with discovery service")
                # Do not raise, just warn
    except Exception as e:
        logger.warning("Startup: Could not register with discovery service", error=str(e))
        # Do not raise, just warn

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "edge-service"}

# Static files and templates for web interface
try:
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "static")
    templates_dir = os.path.join(current_dir, "templates")
    
    logger.info("Current directory", current_dir=current_dir)
    logger.info("Static directory", static_dir=static_dir)
    logger.info("Templates directory", templates_dir=templates_dir)
    
    # Check if static directory exists
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        logger.info("Static files mounted successfully")
    else:
        logger.warning("Static directory not found", static_dir=static_dir)
    
    # Check if templates directory exists
    if os.path.exists(templates_dir):
        templates = Jinja2Templates(directory=templates_dir)
        logger.info("Templates directory found")
        
        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            """Serve the main application page."""
            return templates.TemplateResponse("index.html", {"request": request})
        
        @app.get("/application", response_class=HTMLResponse)
        async def application_page(request: Request):
            """Serve the application page."""
            return templates.TemplateResponse("application.html", {"request": request})
        
        @app.get("/application_list", response_class=HTMLResponse)
        async def application_list_page(request: Request):
            """Serve the application list page."""
            return templates.TemplateResponse("application_list.html", {"request": request})
    else:
        logger.warning("Templates directory not found")
        
        @app.get("/")
        async def fallback_index():
            """Fallback index page."""
            return {"message": "Edge Service is running", "status": "healthy"}
        
except Exception as e:
    logger.warning("Static files and templates not available", error=str(e))
    
    @app.get("/")
    async def fallback_index():
        """Fallback index page."""
        return {"message": "Edge Service is running", "status": "healthy"}

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def route_request(
    path: str,
    request: Request,
    token_data: Optional[Dict] = Depends(validate_token_dependency)
):
    """Route requests to appropriate services."""
    # Skip routing for root path and static files - these should be handled by the frontend
    if path == "" or path == "/" or path.startswith("static/") or path.startswith("docs"):
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Determine target service
    service_name = get_service_name_from_path(path)
    if not service_name:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Get request body
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    # Prepare headers (remove host header to avoid conflicts)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Route the request
    logger.info("Routing request", 
               method=request.method, 
               path=path, 
               service=service_name)
    
    return await service_discovery.route_request(
        service_name=service_name,
        path=path,
        method=request.method,
        headers=headers,
        body=body
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 