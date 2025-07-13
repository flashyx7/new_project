from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import consul
import structlog
import os
import json

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
    title="Config Service",
    description="Configuration management service",
    version="1.0.0"
)

# Consul client
consul_host = os.getenv("CONSUL_HOST", "localhost")
consul_port = int(os.getenv("CONSUL_PORT", "8500"))
consul_client = consul.Consul(host=consul_host, port=consul_port)

# Default configurations for each service
DEFAULT_CONFIGS = {
    "auth-service": {
        "database": {
            "url": "mysql://recruitment_user:recruitment_pass@mysql:3306/recruitment_system"
        },
        "jwt": {
            "secret_key": "your-secret-key-here-change-in-production",
            "algorithm": "HS256",
            "expire_minutes": 30
        },
        "server": {
            "port": 8081
        }
    },
    "registration-service": {
        "database": {
            "url": "mysql://recruitment_user:recruitment_pass@mysql:3306/recruitment_system"
        },
        "server": {
            "port": 8888
        }
    },
    "job-application-service": {
        "database": {
            "url": "mysql://recruitment_user:recruitment_pass@mysql:3306/recruitment_system"
        },
        "server": {
            "port": 8082
        },
        "pagination": {
            "default_page_size": 10,
            "max_page_size": 100
        }
    },
    "edge-service": {
        "server": {
            "port": 8080
        },
        "cors": {
            "allowed_origins": ["*"],
            "allowed_methods": ["*"],
            "allowed_headers": ["*"]
        }
    }
}

class ConfigUpdate(BaseModel):
    config: Dict[str, Any]

def get_auth_headers():
    """Get authentication headers from request."""
    # In a real implementation, you would validate JWT tokens here
    return {"username": "config-service", "password": "config-password"}

@app.on_event("startup")
async def startup_event():
    """Initialize the config service."""
    logger.info("Config service starting up")
    try:
        # Test Consul connection
        consul_client.agent.self()
        logger.info("Successfully connected to Consul", host=consul_host, port=consul_port)
        
        # Initialize default configurations in Consul
        for service_name, config in DEFAULT_CONFIGS.items():
            key = f"config/{service_name}"
            consul_client.kv.put(key, json.dumps(config))
            logger.info("Initialized default config", service_name=service_name)
            
    except Exception as e:
        logger.error("Failed to connect to Consul", error=str(e))
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "config-service"}

@app.get("/config/{service_name}")
async def get_config(service_name: str, auth: Dict = Depends(get_auth_headers)):
    """Get configuration for a specific service."""
    try:
        key = f"config/{service_name}"
        index, data = consul_client.kv.get(key)
        
        if data is None:
            # Return default config if not found
            default_config = DEFAULT_CONFIGS.get(service_name, {})
            logger.info("Config not found, returning default", service_name=service_name)
            return {"service": service_name, "config": default_config}
        
        config = json.loads(data["Value"].decode("utf-8"))
        logger.info("Retrieved config", service_name=service_name)
        return {"service": service_name, "config": config}
        
    except Exception as e:
        logger.error("Failed to get config", service_name=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/config/{service_name}")
async def update_config(service_name: str, config_update: ConfigUpdate, auth: Dict = Depends(get_auth_headers)):
    """Update configuration for a specific service."""
    try:
        key = f"config/{service_name}"
        success = consul_client.kv.put(key, json.dumps(config_update.config))
        
        if success:
            logger.info("Config updated successfully", service_name=service_name)
            return {"status": "updated", "service": service_name}
        else:
            raise HTTPException(status_code=500, detail="Failed to update configuration")
            
    except Exception as e:
        logger.error("Failed to update config", service_name=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/config/{service_name}")
async def delete_config(service_name: str, auth: Dict = Depends(get_auth_headers)):
    """Delete configuration for a specific service."""
    try:
        key = f"config/{service_name}"
        success = consul_client.kv.delete(key)
        
        if success:
            logger.info("Config deleted successfully", service_name=service_name)
            return {"status": "deleted", "service": service_name}
        else:
            raise HTTPException(status_code=404, detail="Configuration not found")
            
    except Exception as e:
        logger.error("Failed to delete config", service_name=service_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def list_configs(auth: Dict = Depends(get_auth_headers)):
    """List all available configurations."""
    try:
        index, data = consul_client.kv.get("config/", recurse=True)
        
        configs = {}
        if data:
            for item in data:
                service_name = item["Key"].replace("config/", "")
                config = json.loads(item["Value"].decode("utf-8"))
                configs[service_name] = config
        
        logger.info("Retrieved all configs", count=len(configs))
        return {"configs": configs}
        
    except Exception as e:
        logger.error("Failed to list configs", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9999) 