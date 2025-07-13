from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import consul
import structlog
import os
from datetime import datetime

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
    title="Discovery Service",
    description="Service discovery and registration service",
    version="1.0.0"
)

# Consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
consul_port = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=consul_host, port=consul_port)

class ServiceRegistration(BaseModel):
    service_name: str
    service_id: str
    address: str
    port: int
    tags: List[str] = []
    meta: Dict[str, str] = {}

class ServiceInfo(BaseModel):
    service_id: str
    service_name: str
    address: str
    port: int
    tags: List[str]
    meta: Dict[str, str]
    status: str
    last_seen: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize the discovery service."""
    logger.info("Discovery service starting up")
    try:
        # Test Consul connection
        consul_client.agent.self()
        logger.info("Successfully connected to Consul", host=consul_host, port=consul_port)
    except Exception as e:
        logger.error("Failed to connect to Consul", error=str(e))
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "discovery-service"}

@app.post("/register")
async def register_service(service: ServiceRegistration):
    """Register a new service with Consul."""
    try:
        # Register service with Consul (without health check for now)
        success = consul_client.agent.service.register(
            name=service.service_name,
            service_id=service.service_id,
            address=service.address,
            port=service.port,
            tags=service.tags
        )
        
        if success:
            logger.info("Service registered successfully", 
                       service_name=service.service_name,
                       service_id=service.service_id)
            return {"status": "registered", "service_id": service.service_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to register service")
            
    except Exception as e:
        logger.error("Failed to register service", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/deregister/{service_id}")
async def deregister_service(service_id: str):
    """Deregister a service from Consul."""
    try:
        success = consul_client.agent.service.deregister(service_id)
        if success:
            logger.info("Service deregistered successfully", service_id=service_id)
            return {"status": "deregistered", "service_id": service_id}
        else:
            raise HTTPException(status_code=404, detail="Service not found")
    except Exception as e:
        logger.error("Failed to deregister service", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services")
async def list_services():
    """List all registered services."""
    try:
        services = consul_client.agent.services()
        service_list = []
        
        for service_id, service_info in services.items():
            service_list.append(ServiceInfo(
                service_id=service_id,
                service_name=service_info.get("Service", ""),
                address=service_info.get("Address", ""),
                port=service_info.get("Port", 0),
                tags=service_info.get("Tags", []),
                meta=service_info.get("Meta", {}),
                status=service_info.get("Status", "unknown"),
                last_seen=datetime.utcnow()
            ))
        
        return {"services": service_list}
    except Exception as e:
        logger.error("Failed to list services", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/{service_name}")
async def get_service_instances(service_name: str):
    """Get all instances of a specific service."""
    try:
        # Get all services from Consul agent
        all_services = consul_client.agent.services()
        instances = []
        
        for service_id, service_info in all_services.items():
            if service_info.get("Service") == service_name:
                instances.append({
                    "service_id": service_info.get("ID"),
                    "service_name": service_info.get("Service"),
                    "address": service_info.get("Address"),
                    "port": service_info.get("Port"),
                    "tags": service_info.get("Tags", []),
                    "meta": service_info.get("Meta", {}),
                    "status": "passing"  # Assume passing for now
                })
        
        return {"service_name": service_name, "instances": instances}
    except Exception as e:
        logger.error("Failed to get service instances", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090) 