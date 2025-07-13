#!/usr/bin/env python3
"""
Start all microservices for the Recruitment System.
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

class ServiceManager:
    """Manage microservices."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.service_configs = {
            "discovery-service": {
                "command": ["python", "discovery_service/main.py"],
                "port": 9090,
                "health_url": "http://localhost:9090/health"
            },
            "config-service": {
                "command": ["python", "config_service/main.py"],
                "port": 9999,
                "health_url": "http://localhost:9999/health"
            },
            "auth-service": {
                "command": ["python", "auth_service/main.py"],
                "port": 8081,
                "health_url": "http://localhost:8081/health"
            },
            "registration-service": {
                "command": ["python", "registration_service/main.py"],
                "port": 8888,
                "health_url": "http://localhost:8888/health"
            },
            "job-application-service": {
                "command": ["python", "job_application_service/main.py"],
                "port": 8082,
                "health_url": "http://localhost:8082/health"
            },
            "edge-service": {
                "command": ["python", "edge_service/main.py"],
                "port": 8080,
                "health_url": "http://localhost:8080/health"
            }
        }
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available."""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def kill_process_on_port(self, port: int) -> bool:
        """Kill process using a specific port using netstat and taskkill."""
        try:
            # Use netstat to find process using the port
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Could not run netstat to check port {port}")
                return False
            
            # Parse netstat output to find process using the port
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            # Kill the process
                            subprocess.run(
                                ["taskkill", "/PID", pid, "/F"], 
                                capture_output=True, 
                                shell=True
                            )
                            logger.info(f"Killed process {pid} on port {port}")
                            return True
                        except Exception as e:
                            logger.error(f"Failed to kill process {pid}", error=str(e))
                            continue
            
            return False
        except Exception as e:
            logger.error(f"Failed to kill process on port {port}", error=str(e))
            return False
    
    async def start_service(self, service_name: str) -> bool:
        """Start a single service."""
        config = self.service_configs[service_name]
        port = config["port"]
        
        # Check if port is available
        if not self.check_port_available(port):
            logger.warning(f"Port {port} is already in use for {service_name}")
            if self.kill_process_on_port(port):
                logger.info(f"Killed process on port {port}")
                await asyncio.sleep(2)  # Wait for port to be released
            else:
                logger.error(f"Could not free port {port} for {service_name}")
                return False
        
        try:
            logger.info(f"Starting {service_name} on port {port}")
            
            # Start the service
            process = subprocess.Popen(
                config["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = process
            
            # Wait a bit for the service to start
            await asyncio.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"{service_name} started successfully", pid=process.pid)
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"{service_name} failed to start", 
                           stdout=stdout, stderr=stderr, return_code=process.returncode)
                return False
                
        except Exception as e:
            logger.error(f"Failed to start {service_name}", error=str(e))
            return False
    
    async def start_all_services(self) -> bool:
        """Start all services in the correct order."""
        logger.info("Starting all microservices")
        
        # Start services in dependency order
        startup_order = [
            "discovery-service",
            "config-service", 
            "auth-service",
            "registration-service",
            "job-application-service",
            "edge-service"
        ]
        
        for service_name in startup_order:
            success = await self.start_service(service_name)
            if not success:
                logger.error(f"Failed to start {service_name}, stopping all services")
                await self.stop_all_services()
                return False
            
            # Wait between services
            await asyncio.sleep(2)
        
        logger.info("All services started successfully")
        return True
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a single service."""
        if service_name not in self.processes:
            logger.warning(f"Service {service_name} not found in running processes")
            return True
        
        process = self.processes[service_name]
        try:
            logger.info(f"Stopping {service_name}")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                logger.info(f"{service_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"{service_name} did not stop gracefully, forcing kill")
                process.kill()
                process.wait()
            
            del self.processes[service_name]
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop {service_name}", error=str(e))
            return False
    
    async def stop_all_services(self):
        """Stop all running services."""
        logger.info("Stopping all services")
        
        for service_name in list(self.processes.keys()):
            await self.stop_service(service_name)
        
        logger.info("All services stopped")
    
    def get_service_status(self) -> Dict[str, str]:
        """Get status of all services."""
        status = {}
        for service_name, process in self.processes.items():
            if process.poll() is None:
                status[service_name] = "running"
            else:
                status[service_name] = "stopped"
        return status
    
    async def monitor_services(self):
        """Monitor running services."""
        logger.info("Starting service monitoring")
        
        while True:
            try:
                status = self.get_service_status()
                for service_name, service_status in status.items():
                    if service_status == "stopped":
                        logger.warning(f"Service {service_name} has stopped unexpectedly")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error("Error during service monitoring", error=str(e))
                await asyncio.sleep(5)

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    sys.exit(0)

async def main():
    """Main function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    service_manager = ServiceManager()
    
    try:
        # Start all services
        success = await service_manager.start_all_services()
        
        if success:
            logger.info("All services started successfully")
            
            # Monitor services
            await service_manager.monitor_services()
        else:
            logger.error("Failed to start all services")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
    finally:
        # Clean up
        await service_manager.stop_all_services()

if __name__ == "__main__":
    asyncio.run(main()) 