
#!/usr/bin/env python3
"""
Simplified startup script for the Recruitment System.
Starts the edge service which includes the frontend and backend API.
"""

import subprocess
import sys
import time
import os

def check_dependencies():
    """Check and install dependencies."""
    print("🔍 Checking dependencies...")
    try:
        result = subprocess.run([sys.executable, "check_dependencies.py"], 
                              capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("Warnings:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"⚠ Dependency check failed: {e}")
        return False

def main():
    """Start the recruitment system."""
    print("🚀 Starting Recruitment System...")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("⚠️  Installing missing dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "itsdangerous==2.1.2"], 
                         check=True, timeout=30)
            print("✅ Dependencies installed")
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
    
    # Initialize database first
    print("\n1. Initializing database...")
    try:
        result = subprocess.run([sys.executable, "scripts/init_database.py"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓ Database initialized successfully")
        else:
            print("⚠ Database initialization failed, but continuing...")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"⚠ Database initialization error: {e}")
        print("Continuing anyway...")
    
    # Start edge service (includes frontend and API gateway)
    print("\n2. Starting edge service...")
    try:
        # Set environment variables
        os.environ['HOST'] = '0.0.0.0'
        os.environ['PORT'] = '8080'
        
        print("🌐 Frontend and backend will be available at:")
        print("   http://localhost:8080")
        print("📱 Use the following test credentials:")
        print("   Username: admin, Password: admin123 (Admin)")
        print("   Username: jcandidate, Password: candidate123 (Applicant)")
        print("   Username: jrecruiter, Password: recruiter123 (Recruiter)")
        print("\n" + "=" * 50)
        print("🚀 Starting server...")
        
        # Start the edge service
        subprocess.run([sys.executable, "edge_service/main.py"])
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error starting edge service: {e}")
        print("Traceback:")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
