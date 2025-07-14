
"""
Edge Service - Main entry point for the Recruitment System
Handles routing, authentication, and serves the web interface
"""

import os
import sys
import sqlite3
import structlog
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared.security import verify_password, create_access_token, verify_token

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

# FastAPI app
app = FastAPI(
    title="Recruitment System",
    description="Edge Service for Recruitment Tracking System",
    version="1.0.0"
)

# Add session middleware first
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-here-change-in-production")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="edge_service/static"), name="static")
templates = Jinja2Templates(directory="edge_service/templates")

# Database helper functions
def get_db_connection():
    """Get database connection."""
    return sqlite3.connect("recruitment_system.db")

def authenticate_user(username: str, password: str):
    """Authenticate user credentials."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT c.id, c.person_id, c.username, c.password, p.firstname, p.lastname, p.email, p.role_id
            FROM credential c
            JOIN person p ON c.person_id = p.id
            WHERE c.username = ?
        """, (username,))

        user = cursor.fetchone()
        conn.close()

        if user and verify_password(password, user[3]):
            return {
                "id": user[0],
                "person_id": user[1],
                "username": user[2],
                "firstname": user[4],
                "lastname": user[5],
                "email": user[6],
                "role_id": user[7]
            }
        return None

    except Exception as e:
        logger.error("Authentication failed", error=str(e))
        return None

def get_current_user(request: Request):
    """Get current user from session or token."""
    # Check session first
    user_id = request.session.get("user_id")
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.id, c.person_id, c.username, p.firstname, p.lastname, p.email, p.role_id
                FROM credential c
                JOIN person p ON c.person_id = p.id
                WHERE c.id = ?
            """, (user_id,))

            user = cursor.fetchone()
            conn.close()

            if user:
                return {
                    "id": user[0],
                    "person_id": user[1],
                    "username": user[2],
                    "firstname": user[3],
                    "lastname": user[4],
                    "email": user[5],
                    "role_id": user[6]
                }
        except Exception as e:
            logger.error("User lookup failed", error=str(e))

    return None

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login."""
    user = authenticate_user(username, password)

    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "error": "Invalid username or password"
        })

    # Create session
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]

    # Redirect to dashboard
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page."""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...)
):
    """Handle registration."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT id FROM credential WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Username already exists"
            })

        cursor.execute("SELECT id FROM person WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "Email already exists"
            })

        # Create person
        cursor.execute("""
            INSERT INTO person (firstname, lastname, email, role_id)
            VALUES (?, ?, ?, ?)
        """, (firstname, lastname, email, 2))  # Default to Applicant role

        person_id = cursor.lastrowid

        # Create credential
        from shared.security import get_password_hash
        hashed_password = get_password_hash(password)
        cursor.execute("""
            INSERT INTO credential (person_id, username, password)
            VALUES (?, ?, ?)
        """, (person_id, username, hashed_password))

        conn.commit()
        conn.close()

        return RedirectResponse(url="/login?message=Registration successful", status_code=302)

    except Exception as e:
        logger.error("Registration failed", error=str(e))
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Registration failed. Please try again."
        })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get statistics
        cursor.execute("SELECT COUNT(*) FROM job_posting WHERE status = 'active'")
        active_jobs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM application")
        total_applications = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM person WHERE role_id = 2")
        total_candidates = cursor.fetchone()[0]

        # Get recent applications for this user
        recent_applications = []
        if user["role_id"] == 2:  # Applicant
            cursor.execute("""
                SELECT a.id, jp.title, a.date_of_registration, s.name as status
                FROM application a
                JOIN job_posting jp ON a.job_posting_id = jp.id
                JOIN status s ON a.status_id = s.id
                WHERE a.person_id = ?
                ORDER BY a.date_of_registration DESC
                LIMIT 5
            """, (user["person_id"],))
            recent_applications = cursor.fetchall()

        conn.close()

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "stats": {
                "active_jobs": active_jobs,
                "total_applications": total_applications,
                "total_candidates": total_candidates
            },
            "recent_applications": recent_applications
        })

    except Exception as e:
        logger.error("Dashboard error", error=str(e))
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "error": "Unable to load dashboard data"
        })

@app.get("/jobs", response_class=HTMLResponse)
async def jobs_page(request: Request):
    """Jobs listing page."""
    user = get_current_user(request)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT jp.id, jp.title, jp.description, jp.location, jp.salary_min, jp.salary_max,
                   jp.employment_type, jp.experience_level, jc.name as category
            FROM job_posting jp
            LEFT JOIN job_category jc ON jp.category_id = jc.id
            WHERE jp.status = 'active'
            ORDER BY jp.created_at DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "user": user,
            "jobs": jobs
        })

    except Exception as e:
        logger.error("Jobs page error", error=str(e))
        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "user": user,
            "error": "Unable to load jobs"
        })

@app.post("/jobs/{job_id}/apply")
async def apply_to_job(request: Request, job_id: int, cover_letter: str = Form(...)):
    """Apply to a job."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if already applied
        cursor.execute(
            "SELECT id FROM application WHERE person_id = ? AND job_posting_id = ?",
            (user["person_id"], job_id)
        )
        
        if cursor.fetchone():
            conn.close()
            return JSONResponse(
                status_code=409,
                content={"detail": "You have already applied to this job"}
            )

        # Create application
        cursor.execute("""
            INSERT INTO application (person_id, job_posting_id, cover_letter, status_id)
            VALUES (?, ?, ?, ?)
        """, (user["person_id"], job_id, cover_letter, 1))  # 1 = submitted status

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={"message": "Application submitted successfully"}
        )

    except Exception as e:
        logger.error("Application submission failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"detail": "Application submission failed"}
        )

@app.get("/logout")
async def logout(request: Request):
    """Logout user."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()

        if result and result[0] == 1:
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            return {"status": "unhealthy", "error": "Database check failed"}

    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Error handler for unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn

    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))

    print(f"🚀 Starting Edge Service on {host}:{port}")
    print("📱 Frontend and Backend API available")
    print("=" * 50)

    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start edge service: {e}")
        sys.exit(1)
