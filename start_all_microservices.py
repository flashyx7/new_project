
#!/usr/bin/env python3
"""
Complete startup script for all recruitment system microservices.
"""

import asyncio
import subprocess
import signal
import sys
import os
import time
import structlog
from typing import Dict, List, Optional

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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

class MicroserviceManager:
    """Manage all microservices."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_configs = {
            "discovery-service": {
                "command": ["python", "discovery_service/main.py"],
                "port": 9090,
                "startup_delay": 2
            },
            "config-service": {
                "command": ["python", "config_service/main.py"],
                "port": 9999,
                "startup_delay": 2
            },
            "auth-service": {
                "command": ["python", "auth_service/main.py"],
                "port": 8081,
                "startup_delay": 3
            },
            "registration-service": {
                "command": ["python", "registration_service/main.py"],
                "port": 8888,
                "startup_delay": 3
            },
            "job-application-service": {
                "command": ["python", "job_application_service/main.py"],
                "port": 8082,
                "startup_delay": 3
            },
            "edge-service": {
                "command": ["python", "edge_service/main.py"],
                "port": 8080,
                "startup_delay": 5  # Start last to ensure other services are ready
            }
        }
    
    def check_dependencies(self):
        """Check system dependencies."""
        print("🔍 Checking dependencies...")
        try:
            result = subprocess.run([sys.executable, "check_dependencies.py"], 
                                  capture_output=True, text=True, timeout=30)
            print(result.stdout)
            if result.stderr:
                print("Warnings:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"⚠ Dependency check failed: {e}")
            return False
    
    def init_database(self):
        """Initialize the database."""
        print("🗄️  Initializing database...")
        try:
            result = subprocess.run([sys.executable, "scripts/init_database.py"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ Database initialized successfully")
                return True
            else:
                print("⚠ Database initialization failed")
                print(f"Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"⚠ Database initialization error: {e}")
            return False
    
    async def start_service(self, service_name: str) -> bool:
        """Start a single service."""
        config = self.service_configs[service_name]
        
        try:
            logger.info(f"Starting {service_name} on port {config['port']}")
            
            # Set environment variables
            env = os.environ.copy()
            env['HOST'] = '0.0.0.0'
            env['PORT'] = str(config['port'])
            
            # Start the service
            process = subprocess.Popen(
                config["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.processes[service_name] = process
            
            # Wait for startup
            await asyncio.sleep(config["startup_delay"])
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✓ {service_name} started successfully", pid=process.pid)
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service_name} failed to start", 
                           stdout=stdout, stderr=stderr, return_code=process.returncode)
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}", error=str(e))
            return False
    
    async def start_all_services(self) -> bool:
        """Start all services in dependency order."""
        print("🚀 Starting all microservices...")
        
        # Check dependencies
        if not self.check_dependencies():
            print("⚠️  Some dependencies are missing, but continuing...")
        
        # Initialize database
        if not self.init_database():
            print("⚠️  Database initialization had issues, but continuing...")
        
        # Start services in order
        startup_order = [
            "discovery-service",
            "config-service", 
            "auth-service",
            "registration-service",
            "job-application-service",
            "edge-service"
        ]
        
        for service_name in startup_order:
            print(f"\n📦 Starting {service_name}...")
            success = await self.start_service(service_name)
            if not success:
                print(f"⚠️  {service_name} failed to start, but continuing...")
                # Don't stop all services if one fails - continue with others
        
        print("\n" + "=" * 60)
        print("🎉 Microservices startup complete!")
        print("🌐 Access the application at: http://localhost:8080")
        print("📊 Service status:")
        
        for service_name, config in self.service_configs.items():
            if service_name in self.processes and self.processes[service_name].poll() is None:
                print(f"  ✓ {service_name} - Running on port {config['port']}")
            else:
                print(f"  ⚠ {service_name} - Not running")
        
        print("=" * 60)
        return True
    
    async def stop_service(self, service_name: str):
        """Stop a single service."""
        if service_name not in self.processes:
            return
        
        process = self.processes[service_name]
        try:
            logger.info(f"Stopping {service_name}")
            process.terminate()
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            
            del self.processes[service_name]
            
        except Exception as e:
            logger.error(f"Failed to stop {service_name}", error=str(e))
    
    async def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services")
        
        for service_name in list(self.processes.keys()):
            await self.stop_service(service_name)
        
        logger.info("All services stopped")
    
    async def monitor_services(self):
        """Monitor running services."""
        logger.info("Starting service monitoring")
        
        try:
            while True:
                await asyncio.sleep(30)
                
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        logger.warning(f"Service {service_name} has stopped")
                        
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted")

async def main():
    """Main function."""
    manager = MicroserviceManager()
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await manager.start_all_services()
        await manager.monitor_services()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all services...")
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
    finally:
        await manager.stop_all_services()

if __name__ == "__main__":
    asyncio.run(main())
