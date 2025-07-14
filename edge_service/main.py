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

try:
    from shared.security import verify_password, create_access_token, verify_token, get_password_hash
    print("✓ Successfully imported security module")
except ImportError as e:
    print(f"Warning: Could not import security module: {e}")
    print("Using fallback security functions...")
    # Fallback security functions
    import bcrypt
    import jwt
    from datetime import datetime, timedelta

    def get_password_hash(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            return False

    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, "secret-key", algorithm="HS256")

    def verify_token(token: str) -> dict:
        try:
            return jwt.decode(token, "secret-key", algorithms=["HS256"])
        except:
            return None

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
            SELECT c.id, c.person_id, c.username, c.password, 
                   p.firstname, p.lastname, p.email, p.role_id
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
    """Dashboard page with role-based content."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get role-specific dashboard data
        dashboard_data = {}

        if user["role_id"] == 1:  # Admin
            cursor.execute("SELECT COUNT(*) FROM job_posting WHERE status = 'active'")
            dashboard_data["active_jobs"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM application")
            dashboard_data["total_applications"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM person WHERE role_id = 2")
            dashboard_data["total_candidates"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM person WHERE role_id = 3")
            dashboard_data["total_recruiters"] = cursor.fetchone()[0]

            # Recent system activity
            cursor.execute("""
                SELECT p.firstname, p.lastname, jp.title, a.applied_date
                FROM application a
                JOIN person p ON a.person_id = p.id
                JOIN job_posting jp ON a.job_posting_id = jp.id
                ORDER BY a.applied_date DESC
                LIMIT 10
            """)
            dashboard_data["recent_activity"] = cursor.fetchall()

        elif user["role_id"] == 2:  # Applicant
            cursor.execute("SELECT COUNT(*) FROM job_posting WHERE status = 'active'")
            dashboard_data["active_jobs"] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM application WHERE person_id = ?", (user["person_id"],))
            dashboard_data["my_applications"] = cursor.fetchone()[0]

            # My recent applications
            cursor.execute("""
                SELECT jp.title, a.applied_date, ast.name as status
                FROM application a
                JOIN job_posting jp ON a.job_posting_id = jp.id
                JOIN application_status ast ON a.status_id = ast.id
                WHERE a.person_id = ?
                ORDER BY a.applied_date DESC
                LIMIT 5
            """, (user["person_id"],))
            dashboard_data["recent_applications"] = cursor.fetchall()

            # Recommended jobs (job matches)
            cursor.execute("""
                SELECT id, title, description, location, employment_type, salary_min, salary_max
                FROM job_posting 
                WHERE status = 'active'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            dashboard_data["recommended_jobs"] = cursor.fetchall()
            dashboard_data["job_matches"] = len(dashboard_data["recommended_jobs"])

        elif user["role_id"] == 3:  # Recruiter
            cursor.execute("SELECT COUNT(*) FROM job_posting WHERE posted_by = ?", (user["person_id"],))
            dashboard_data["my_job_postings"] = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM application a
                JOIN job_posting jp ON a.job_posting_id = jp.id
                WHERE jp.posted_by = ?
            """, (user["person_id"],))
            dashboard_data["applications_received"] = cursor.fetchone()[0]

            # Recent applications to my jobs
            cursor.execute("""
                SELECT p.firstname, p.lastname, jp.title, a.applied_date, ast.name as status
                FROM application a
                JOIN person p ON a.person_id = p.id
                JOIN job_posting jp ON a.job_posting_id = jp.id
                JOIN application_status ast ON a.status_id = ast.id
                WHERE jp.posted_by = ?
                ORDER BY a.applied_date DESC
                LIMIT 10
            """, (user["person_id"],))
            dashboard_data["recent_applications"] = cursor.fetchall()

        conn.close()

        # Choose template based on role
        if user["role_id"] == 1:  # Admin
            template_name = "admin_dashboard.html"
        elif user["role_id"] == 3:  # Recruiter
            template_name = "recruiter_dashboard.html"
        elif user["role_id"] == 2:  # Applicant
            template_name = "dashboard.html"
        else:
            template_name = "dashboard.html"  # Default fallback

        return templates.TemplateResponse(template_name, {
            "request": request,
            "user": user,
            "dashboard_data": dashboard_data
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
            SELECT j.id, j.title, j.description, j.location, j.salary_min, j.salary_max,
                   j.employment_type, j.experience_level, c.name as category
            FROM job_posting j
            LEFT JOIN job_category c ON j.category_id = c.id
            WHERE j.status = 'active'
            ORDER BY j.created_at DESC
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

# API Routes for frontend JavaScript calls
@app.get("/api/jobs")
async def api_get_jobs():
    """API endpoint to get all active jobs."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.id, j.title, j.description, j.location, j.salary_min, j.salary_max,
                   j.employment_type, j.experience_level, c.name as category
            FROM job_posting j
            LEFT JOIN job_category c ON j.category_id = c.id
            WHERE j.status = 'active'
            ORDER BY j.created_at DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        jobs_list = []
        for job in jobs:
            jobs_list.append({
                "id": job[0],
                "title": job[1],
                "description": job[2],
                "location": job[3],
                "salary_min": job[4],
                "salary_max": job[5],
                "employment_type": job[6],
                "experience_level": job[7],
                "category": job[8]
            })

        return {"jobs": jobs_list}

    except Exception as e:
        logger.error("API Jobs error", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Unable to load jobs"}
        )

@app.post("/api/auth/login")
async def api_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """API endpoint for login."""
    user = authenticate_user(username, password)

    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid username or password"}
        )

    # Create session
    request.session["user_id"] = user["id"]
    request.session["username"] = user["username"]

    # Create access token
    token = create_access_token({"user_id": user["id"], "username": user["username"]})

    return JSONResponse(
        status_code=200,
        content={
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "firstname": user["firstname"],
                "lastname": user["lastname"],
                "email": user["email"],
                "role_id": user["role_id"]
            }
        }
    )

@app.post("/api/auth/register")
async def api_register(request: Request):
    """API endpoint for registration."""
    try:
        form_data = await request.form()
        username = form_data.get("username")
        password = form_data.get("password")
        email = form_data.get("email")
        firstname = form_data.get("firstname")
        lastname = form_data.get("lastname")

        if not all([username, password, email, firstname, lastname]):
            return JSONResponse(
                status_code=400,
                content={"error": "All fields are required"}
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists
        cursor.execute("SELECT id FROM credential WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return JSONResponse(
                status_code=409,
                content={"error": "Username already exists"}
            )

        cursor.execute("SELECT id FROM person WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return JSONResponse(
                status_code=409,
                content={"error": "Email already exists"}
            )

        # Create person
        cursor.execute("""
            INSERT INTO person (firstname, lastname, email, role_id)
            VALUES (?, ?, ?, ?)
        """, (firstname, lastname, email, 2))  # Default to Applicant role

        person_id = cursor.lastrowid

        # Create credential
        hashed_password = get_password_hash(password)
        cursor.execute("""
            INSERT INTO credential (person_id, username, password)
            VALUES (?, ?, ?)
        """, (person_id, username, hashed_password))

        conn.commit()
        conn.close()

        logger.info("User registered successfully", username=username)

        return JSONResponse(
            status_code=201,
            content={"message": "Registration successful"}
        )

    except Exception as e:
        logger.error("API Registration failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Registration failed. Please try again."}
        )

@app.get("/api/user/profile")
async def api_get_user_profile(request: Request):
    """API endpoint to get user profile."""
    user = get_current_user(request)
    if not user:
        return JSONResponse(
            status_code=401,
            content={"error": "Not authenticated"}
        )

    return JSONResponse(
        status_code=200,
        content={"user": user}
    )

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

# Recruiter routes
@app.get("/recruiter/post-job", response_class=HTMLResponse)
async def post_job_page(request: Request):
    """Post new job page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 3:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("post_job.html", {"request": request, "user": user})

@app.post("/recruiter/post-job")
async def create_job_posting(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    salary_min: float = Form(None),
    salary_max: float = Form(None),
    employment_type: str = Form(...),
    experience_level: str = Form(...)
):
    """Create a new job posting."""
    user = get_current_user(request)
    if not user or user["role_id"] != 3:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO job_posting (title, description, location, salary_min, salary_max, 
                                   employment_type, experience_level, posted_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (title, description, location, salary_min, salary_max, employment_type, experience_level, user["person_id"]))

        conn.commit()
        conn.close()

        return RedirectResponse(url="/recruiter/my-jobs?success=Job posted successfully", status_code=302)

    except Exception as e:
        logger.error("Job posting failed", error=str(e))
        return templates.TemplateResponse("post_job.html", {
            "request": request,
            "user": user,
            "error": "Failed to post job. Please try again."
        })

@app.get("/recruiter/my-jobs", response_class=HTMLResponse)
async def my_jobs_page(request: Request):
    """My job postings page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 3:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, location, salary_min, salary_max, 
                   employment_type, experience_level, status, created_at
            FROM job_posting 
            WHERE posted_by = ?
            ORDER BY created_at DESC
        """, (user["person_id"],))

        jobs = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("my_jobs.html", {
            "request": request,
            "user": user,
            "jobs": jobs
        })

    except Exception as e:
        logger.error("Failed to load jobs", error=str(e))
        return templates.TemplateResponse("my_jobs.html", {
            "request": request,
            "user": user,
            "error": "Failed to load job postings"
        })

@app.get("/recruiter/applications", response_class=HTMLResponse)
async def recruiter_applications(request: Request):
    """View applications for recruiter's jobs."""
    user = get_current_user(request)
    if not user or user["role_id"] != 3:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, p.firstname, p.lastname, jp.title, a.applied_date, 
                   ast.name as status, a.cover_letter
            FROM application a
            JOIN person p ON a.person_id = p.id
            JOIN job_posting jp ON a.job_posting_id = jp.id
            JOIN application_status ast ON a.status_id = ast.id
            WHERE jp.posted_by = ?
            ORDER BY a.applied_date DESC
        """, (user["person_id"],))

        applications = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("recruiter_applications.html", {
            "request": request,
            "user": user,
            "applications": applications
        })

    except Exception as e:
        logger.error("Failed to load applications", error=str(e))
        return templates.TemplateResponse("recruiter_applications.html", {
            "request": request,
            "user": user,
            "error": "Failed to load applications"
        })

@app.get("/recruiter/candidates", response_class=HTMLResponse)
async def browse_candidates(request: Request):
    """Browse candidates page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 3:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.firstname, p.lastname, p.email, 
                   COUNT(a.id) as application_count
            FROM person p
            LEFT JOIN application a ON p.id = a.person_id
            WHERE p.role_id = 2
            GROUP BY p.id, p.firstname, p.lastname, p.email
            ORDER BY p.firstname, p.lastname
        """)

        candidates = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("browse_candidates.html", {
            "request": request,
            "user": user,
            "candidates": candidates
        })

    except Exception as e:
        logger.error("Failed to load candidates", error=str(e))
        return templates.TemplateResponse("browse_candidates.html", {
            "request": request,
            "user": user,
            "error": "Failed to load candidates"
        })

# Applicant routes
@app.get("/applicant/my-applications", response_class=HTMLResponse)
async def my_applications(request: Request):
    """My applications page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 2:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, jp.title, jp.location, jp.employment_type, 
                   a.applied_date, ast.name as status
            FROM application a
            JOIN job_posting jp ON a.job_posting_id = jp.id
            JOIN application_status ast ON a.status_id = ast.id
            WHERE a.person_id = ?
            ORDER BY a.applied_date DESC
        """, (user["person_id"],))

        applications = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("my_applications.html", {
            "request": request,
            "user": user,
            "applications": applications
        })

    except Exception as e:
        logger.error("Failed to load applications", error=str(e))
        return templates.TemplateResponse("my_applications.html", {
            "request": request,
            "user": user,
            "error": "Failed to load applications"
        })

@app.delete("/applicant/applications/{application_id}")
async def delete_application(request: Request, application_id: int):
    """Delete an application."""
    user = get_current_user(request)
    if not user or user["role_id"] != 2:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify the application belongs to the user
        cursor.execute(
            "SELECT id FROM application WHERE id = ? AND person_id = ?",
            (application_id, user["person_id"])
        )

        if not cursor.fetchone():
            conn.close()
            return JSONResponse(
                status_code=404,
                content={"error": "Application not found"}
            )

        # Delete the application
        cursor.execute("DELETE FROM application WHERE id = ? AND person_id = ?", 
                      (application_id, user["person_id"]))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        if rows_affected > 0:
            return JSONResponse(
                status_code=200,
                content={"message": "Application deleted successfully"}
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "Application not found or already deleted"}
            )

    except Exception as e:
        logger.error("Application deletion failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to delete application"}
        )

@app.get("/applicant/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Profile page."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT firstname, lastname, email, date_of_birth, phone, address
            FROM person WHERE id = ?
        """, (user["person_id"],))

        profile = cursor.fetchone()
        conn.close()

        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "profile": profile
        })

@app.post("/applicant/profile")
async def update_profile(
    request: Request,
    firstname: str = Form(...),
    lastname: str = Form(...),
    email: str = Form(...),
    date_of_birth: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None)
):
    """Update user profile."""
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE person 
            SET firstname = ?, lastname = ?, email = ?, date_of_birth = ?, phone = ?, address = ?
            WHERE id = ?
        """, (firstname, lastname, email, date_of_birth, phone, address, user["person_id"]))

        conn.commit()
        conn.close()

        return RedirectResponse(url="/applicant/profile?success=Profile updated successfully", status_code=302)

    except Exception as e:
        logger.error("Profile update failed", error=str(e))
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "error": "Failed to update profile. Please try again."
        })

@app.get("/applicant/job-matches", response_class=HTMLResponse)
async def job_matches(request: Request):
    """Job matches page for applicants."""
    user = get_current_user(request)
    if not user or user["role_id"] != 2:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, title, description, location, employment_type, 
                   salary_min, salary_max, experience_level, created_at
            FROM job_posting 
            WHERE status = 'active'
            ORDER BY created_at DESC
            LIMIT 20
        """)

        jobs = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "user": user,
            "jobs": jobs,
            "page_title": "Job Matches"
        })

    except Exception as e:
        logger.error("Failed to load job matches", error=str(e))
        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "user": user,
            "error": "Failed to load job matches"
        })

@app.get("/job/{job_id}", response_class=HTMLResponse)
async def job_details(request: Request, job_id: int):
    """Job details page."""
    user = get_current_user(request)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.id, j.title, j.description, j.location, j.salary_min, j.salary_max,
                   j.employment_type, j.experience_level, j.requirements, j.created_at,
                   p.firstname, p.lastname
            FROM job_posting j
            JOIN person p ON j.posted_by = p.id
            WHERE j.id = ? AND j.status = 'active'
        """, (job_id,))

        job = cursor.fetchone()

        # Check if user already applied
        applied = False
        if user:
            cursor.execute(
                "SELECT id FROM application WHERE person_id = ? AND job_posting_id = ?",
                (user["person_id"], job_id)
            )
            applied = cursor.fetchone() is not None

        conn.close()

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return templates.TemplateResponse("job_details.html", {
            "request": request,
            "user": user,
            "job": job,
            "applied": applied
        })

    except Exception as e:
        logger.error("Failed to load job details", error=str(e))
        return templates.TemplateResponse("error.html", {
            "request": request,
            "user": user,
            "error": "Job not found"
        })

# Admin routes
@app.get("/admin/users", response_class=HTMLResponse)
async def manage_users(request: Request):
    """Manage users page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.firstname, p.lastname, p.email, r.name as role,
                   c.username, p.created_at
            FROM person p
            JOIN role r ON p.role_id = r.id
            LEFT JOIN credential c ON p.id = c.person_id
            ORDER BY p.created_at DESC
        """)

        users = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("manage_users.html", {
            "request": request,
            "user": user,
            "users": users
        })

    except Exception as e:
        logger.error("Failed to load users", error=str(e))
        return templates.TemplateResponse("manage_users.html", {
            "request": request,
            "user": user,
            "error": "Failed to load users"
        })

@app.get("/admin/users/{user_id}")
async def get_user_details(request: Request, user_id: int):
    """Get user details for editing."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.firstname, p.lastname, p.email, p.role_id, r.name as role_name
            FROM person p
            JOIN role r ON p.role_id = r.id
            WHERE p.id = ?
        """, (user_id,))

        user_data = cursor.fetchone()
        conn.close()

        if not user_data:
            return JSONResponse(status_code=404, content={"error": "User not found"})

        return JSONResponse(status_code=200, content={
            "user": {
                "id": user_data[0],
                "firstname": user_data[1],
                "lastname": user_data[2],
                "email": user_data[3],
                "role_id": user_data[4],
                "role_name": user_data[5]
            }
        })

    except Exception as e:
        logger.error("Get user details failed", error=str(e))
        return JSONResponse(status_code=500, content={"error": "Failed to get user details"})

@app.post("/admin/users/{user_id}/edit")
async def edit_user(request: Request, user_id: int):
    """Edit user details."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})

    try:
        form_data = await request.form()
        firstname = form_data.get("firstname")
        lastname = form_data.get("lastname")
        email = form_data.get("email")
        role_id = form_data.get("role_id")

        if not all([firstname, lastname, email, role_id]):
            return JSONResponse(status_code=400, content={"error": "All fields are required"})

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE person 
            SET firstname = ?, lastname = ?, email = ?, role_id = ?
            WHERE id = ?
        """, (firstname, lastname, email, role_id, user_id))

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={"message": "User updated successfully"}
        )

    except Exception as e:
        logger.error("User edit failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to update user"}
        )

@app.delete("/admin/users/{user_id}")
async def delete_user(request: Request, user_id: int):
    """Delete user."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete user's applications first
        cursor.execute("DELETE FROM application WHERE person_id = ?", (user_id,))

        # Delete user's credentials
        cursor.execute("DELETE FROM credential WHERE person_id = ?", (user_id,))

        # Delete the user
        cursor.execute("DELETE FROM person WHERE id = ?", (user_id,))

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={"message": "User deleted successfully"}
        )

    except Exception as e:
        logger.error("User deletion failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to delete user"}
        )

@app.get("/admin/jobs", response_class=HTMLResponse)
async def manage_jobs(request: Request):
    """Manage jobs page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.id, j.title, j.location, j.employment_type, j.status,
                   p.firstname, p.lastname, j.created_at,
                   COUNT(a.id) as application_count
            FROM job_posting j
            JOIN person p ON j.posted_by = p.id
            LEFT JOIN application a ON j.id = a.job_posting_id
            GROUP BY j.id, j.title, j.location, j.employment_type, j.status,
                     p.firstname, p.lastname, j.created_at
            ORDER BY j.created_at DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("manage_jobs.html", {
            "request": request,
            "user": user,
            "jobs": jobs
        })

    except Exception as e:
        logger.error("Failed to load jobs", error=str(e))
        return templates.TemplateResponse("manage_jobs.html", {
            "request": request,
            "user": user,
            "error": "Failed to load jobs"
        })

@app.get("/admin/jobs/{job_id}/view")
async def view_job_admin(request: Request, job_id: int):
    """View job details for admin."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.*, p.firstname, p.lastname
            FROM job_posting j
            JOIN person p ON j.posted_by = p.id
            WHERE j.id = ?
        """, (job_id,))

        job = cursor.fetchone()
        conn.close()

        if not job:
            return JSONResponse(
                status_code=404,
                content={"error": "Job not found"}
            )

        return JSONResponse(
            status_code=200,
            content={"job": job}
        )

    except Exception as e:
        logger.error("Job view failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to load job"}
        )

@app.post("/admin/jobs/{job_id}/edit")
async def edit_job_admin(request: Request, job_id: int):
    """Edit job for admin."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        form_data = await request.form()
        title = form_data.get("title")
        description = form_data.get("description")
        location = form_data.get("location")
        status = form_data.get("status")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE job_posting 
            SET title = ?, description = ?, location = ?, status = ?
            WHERE id = ?
        """, (title, description, location, status, job_id))

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={"message": "Job updated successfully"}
        )

    except Exception as e:
        logger.error("Job edit failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to update job"}
        )

@app.post("/admin/jobs/{job_id}/deactivate")
async def deactivate_job(request: Request, job_id: int):
    """Deactivate job."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE job_posting 
            SET status = 'inactive'
            WHERE id = ?
        """, (job_id,))

        conn.commit()
        conn.close()

        return JSONResponse(
            status_code=200,
            content={"message": "Job deactivated successfully"}
        )

    except Exception as e:
        logger.error("Job deactivation failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to deactivate job"}
        )

@app.get("/admin/applications", response_class=HTMLResponse)
async def admin_applications(request: Request):
    """View all applications."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, p.firstname, p.lastname, jp.title, 
                   rec.firstname as rec_firstname, rec.lastname as rec_lastname,
                   a.applied_date, ast.name as status
            FROM application a
            JOIN person p ON a.person_id = p.id
            JOIN job_posting jp ON a.job_posting_id = jp.id
            JOIN person rec ON jp.posted_by = rec.id
            JOIN application_status ast ON a.status_id = ast.id
            ORDER BY a.applied_date DESC
        """)

        applications = cursor.fetchall()
        conn.close()

        return templates.TemplateResponse("admin_applications.html", {
            "request": request,
            "user": user,
            "applications": applications
        })

    except Exception as e:
        logger.error("Failed to load applications", error=str(e))
        return templates.TemplateResponse("admin_applications.html", {
            "request": request,
            "user": user,
            "error": "Failed to load applications"
        })

@app.get("/admin/reports", response_class=HTMLResponse)
async def generate_reports(request: Request):
    """Generate reports page."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get statistics for reports
        stats = {}

        cursor.execute("SELECT COUNT(*) FROM person WHERE role_id = 2")
        stats["total_candidates"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM person WHERE role_id = 3")
        stats["total_recruiters"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM job_posting WHERE status = 'active'")
        stats["active_jobs"] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM application")
        stats["total_applications"] = cursor.fetchone()[0]

        # Monthly application stats
        cursor.execute("""
            SELECT strftime('%Y-%m', applied_date) as month, COUNT(*) as count
            FROM application
            GROUP BY strftime('%Y-%m', applied_date)
            ORDER BY month DESC
            LIMIT 12
        """)
        stats["monthly_applications"] = cursor.fetchall()

        conn.close()

        return templates.TemplateResponse("reports.html", {
            "request": request,
            "user": user,
            "stats": stats
        })

    except Exception as e:
        logger.error("Failed to load reports", error=str(e))
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "user": user,
            "error": "Failed to load reports"
        })

@app.get("/admin/export/users")
async def export_users_report(request: Request):
    """Export users report."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.firstname, p.lastname, p.email, r.name as role, p.created_at
            FROM person p
            JOIN role r ON p.role_id = r.id
            ORDER BY p.created_at DESC
        """)

        users = cursor.fetchall()
        conn.close()

        # Generate CSV content
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['First Name', 'Last Name', 'Email', 'Role', 'Created Date'])
        for user_row in users:
            writer.writerow(user_row)

        csv_content = output.getvalue()
        output.close()

        return JSONResponse(
            status_code=200,
            content={"data": csv_content, "filename": "users_report.csv"}
        )

    except Exception as e:
        logger.error("User export failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to export users"}
        )

@app.get("/admin/export/jobs")
async def export_jobs_report(request: Request):
    """Export jobs report."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT j.title, j.location, j.employment_type, j.status, 
                   p.firstname, p.lastname, j.created_at,
                   COUNT(a.id) as application_count
            FROM job_posting j
            JOIN person p ON j.posted_by = p.id
            LEFT JOIN application a ON j.id = a.job_posting_id
            GROUP BY j.id
            ORDER BY j.created_at DESC
        """)

        jobs = cursor.fetchall()
        conn.close()

        # Generate CSV content
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['Title', 'Location', 'Type', 'Status', 'Posted By', 'Created Date', 'Applications'])
        for job in jobs:
            writer.writerow([job[0], job[1], job[2], job[3], f"{job[4]} {job[5]}", job[6], job[7]])

        csv_content = output.getvalue()
        output.close()

        return JSONResponse(
            status_code=200,
            content={"data": csv_content, "filename": "jobs_report.csv"}
        )

    except Exception as e:
        logger.error("Jobs export failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to export jobs"}
        )

@app.get("/admin/export/applications")
async def export_applications_report(request: Request):
    """Export applications report."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.firstname, p.lastname, jp.title, a.applied_date, ast.name as status
            FROM application a
            JOIN person p ON a.person_id = p.id
            JOIN job_posting jp ON a.job_posting_id = jp.id
            JOIN application_status ast ON a.status_id = ast.id
            ORDER BY a.applied_date DESC
        """)

        applications = cursor.fetchall()
        conn.close()

        # Generate CSV content
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['Applicant', 'Job Title', 'Applied Date', 'Status'])
        for app in applications:
            writer.writerow([f"{app[0]} {app[1]}", app[2], app[3], app[4]])

        csv_content = output.getvalue()
        output.close()

        return JSONResponse(
            status_code=200,
            content={"data": csv_content, "filename": "applications_report.csv"}
        )

    except Exception as e:
        logger.error("Applications export failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to export applications"}
        )

@app.get("/admin/analytics")
async def system_analytics(request: Request):
    """Get system analytics."""
    user = get_current_user(request)
    if not user or user["role_id"] != 1:
        return RedirectResponse(url="/login", status_code=302)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        analytics = {}

        # User growth
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM person
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        analytics["user_growth"] = cursor.fetchall()

        # Application trends
        cursor.execute("""
            SELECT DATE(applied_date) as date, COUNT(*) as count
            FROM application
            WHERE applied_date >= date('now', '-30 days')
            GROUP BY DATE(applied_date)
            ORDER BY date
        """)
        analytics["application_trends"] = cursor.fetchall()

        # Job posting trends
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM job_posting
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        analytics["job_trends"] = cursor.fetchall()

        conn.close()

        return JSONResponse(
            status_code=200,
            content={"analytics": analytics}
        )

    except Exception as e:
        logger.error("Analytics failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to load analytics"}
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

# Microservice routing
import httpx

# Service URLs - these would normally come from service discovery
SERVICE_URLS = {
    "auth": "http://localhost:8081",
    "registration": "http://localhost:8888", 
    "job_application": "http://localhost:8082",
    "discovery": "http://localhost:9090",
    "config": "http://localhost:9999"
}

async def route_to_service(service_name: str, path: str, method: str = "GET", **kwargs):
    """Route requests to microservices."""
    if service_name not in SERVICE_URLS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Service {service_name} not found"}
        )

    url = f"{SERVICE_URLS[service_name]}{path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                response = await client.get(url, **kwargs)
            elif method == "POST":
                response = await client.post(url, **kwargs)
            elif method == "PUT":
                response = await client.put(url, **kwargs)
            elif method == "DELETE":
                response = await client.delete(url, **kwargs)
            else:
                return JSONResponse(
                    status_code=405,
                    content={"error": "Method not allowed"}
                )

            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"message": response.text}
            )
    except httpx.TimeoutException:
        logger.error("Service timeout", service=service_name, path=path)
        return JSONResponse(
            status_code=503,
            content={"error": f"Service {service_name} timeout"}
        )
    except httpx.ConnectError:
        logger.warning("Service unavailable", service=service_name, path=path)
        # For now, handle locally if service is unavailable
        return JSONResponse(
            status_code=503,
            content={"error": f"Service {service_name} unavailable"}
        )
    except Exception as e:
        logger.error("Service routing error", service=service_name, path=path, error=str(e))
        return JSONResponse(
            status_code=500,
            content={"error": "Internal routing error"}
        )

# Route to auth service
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_auth(path: str, request: Request):
    """Route authentication requests to auth service."""
    # For now, handle locally since auth service integration is complex
    # This would route to auth service when it's properly set up
    return JSONResponse(
        status_code=501,
        content={"error": "Auth service routing not implemented yet"}
    )

# Route to registration service  
@app.api_route("/api/registration/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_registration(path: str, request: Request):
    """Route registration requests to registration service."""
    try:
        # For now, handle registration locally until service is stable
        if path == "register" and request.method == "POST":
            return await api_register(request)
        return await route_to_service("registration", f"/{path}", request.method)
    except Exception as e:
        logger.error("Registration routing failed", error=str(e))
        # Fallback to local handling
        if path == "register" and request.method == "POST":
            return await api_register(request)
        raise HTTPException(status_code=503, detail="Registration service unavailable")

# Route to job application service
@app.api_route("/api/applications/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_job_applications(path: str, request: Request):
    """Route job application requests to job application service."""
    try:
        return await route_to_service("job_application", f"/{path}", request.method)
    except Exception as e:
        logger.error("Application service routing failed", error=str(e))
        # Local fallback for critical functions
        raise HTTPException(status_code=503, detail="Application service unavailable")

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