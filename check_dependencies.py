
#!/usr/bin/env python3
"""
Dependency checker for the Recruitment System.
Verifies all required packages are installed.
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    'fastapi',
    'uvicorn',
    'pydantic',
    'sqlalchemy',
    'pymysql',
    'cryptography',
    'jose',
    'passlib',
    'httpx',
    'consul',
    'structlog',
    'pytest',
    'dotenv',
    'jinja2',
    'aiofiles',
    'dateutil',
    'orjson',
    'email_validator',
    'healthcheck',
    'slowapi',
    'prometheus_client',
    'sentry_sdk',
    'requests'
]

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []
    installed = []
    
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            installed.append(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    print(f"\nSummary:")
    print(f"✅ Installed: {len(installed)}")
    print(f"❌ Missing: {len(missing)}")
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        return False
    else:
        print("\n🎉 All dependencies are installed!")
        return True

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
