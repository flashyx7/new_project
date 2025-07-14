
#!/usr/bin/env python3
"""
Simplified startup script for the Recruitment System.
Starts the edge service which includes the frontend and backend API.
"""

import subprocess
import sys
import time
import os

def main():
    """Start the recruitment system."""
    print("🚀 Starting Recruitment System...")
    print("=" * 50)
    
    # Initialize database first
    print("1. Initializing database...")
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
        
        # Start the edge service
        subprocess.run([sys.executable, "edge_service/main.py"])
        
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error starting edge service: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
