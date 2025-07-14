
#!/usr/bin/env python3
"""
Check all dependencies for the Recruitment System.
"""

import sys
import importlib
import subprocess

REQUIRED_PACKAGES = [
    'fastapi',
    'uvicorn',
    'jinja2',
    'python_multipart',
    'starlette',
    'aiofiles',
    'structlog',
    'bcrypt',
    'passlib',
    'itsdangerous',
    'sqlalchemy',
    'PyJWT',
    'httpx',
    'requests',
    'pytest',
    'python_dotenv',
    'python_dateutil',
    'email_validator',
    'python_jose'
]

def check_package(package_name):
    """Check if a package is available."""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - MISSING")
        return False

def install_missing_packages():
    """Install missing packages."""
    missing = []
    for package in REQUIRED_PACKAGES:
        if not check_package(package):
            missing.append(package)
    
    if missing:
        print(f"\nInstalling {len(missing)} missing packages...")
        for package in missing:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")

def main():
    """Main function."""
    print("🔍 Checking dependencies...")
    print("=" * 50)
    
    all_good = True
    for package in REQUIRED_PACKAGES:
        if not check_package(package):
            all_good = False
    
    if not all_good:
        print("\n⚠️  Some packages are missing. Installing...")
        install_missing_packages()
    else:
        print("\n✅ All required packages are available")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
