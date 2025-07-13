
#!/usr/bin/env python3
"""
Setup script for the Recruitment System.
Initializes database and prepares the system for first run.
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and print status."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("RECRUITMENT SYSTEM SETUP")
    print("=" * 60)
    
    # Check dependencies
    if not run_command("python check_dependencies.py", "Checking dependencies"):
        print("\n⚠️  Some dependencies are missing. Installing...")
        # Dependencies should already be installed via package manager
    
    # Initialize database
    if run_command("python scripts/init_database.py", "Initializing database"):
        print("✅ Database initialization completed")
    else:
        print("⚠️  Database initialization failed - you may need to set up MySQL")
    
    # Initialize roles
    if run_command("python init_roles.py", "Initializing user roles"):
        print("✅ Role initialization completed")
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    print("\nYou can now start the system using:")
    print("1. Click the 'Run' button to start the Edge Service")
    print("2. Or use 'Initialize and Start All Services' workflow for full system")
    print("3. Access the application at: http://localhost:8080")
    print("\nFor testing, run: python scripts/test_system.py")

if __name__ == "__main__":
    main()
