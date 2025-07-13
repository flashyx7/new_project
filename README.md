# Recruitment System - Python Microservices

A modern, production-ready microservices architecture for recruitment management built with Python and FastAPI.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python scripts/init_database.py
   ```

3. **Start all services:**
   ```bash
   # Windows
   .\start_all_services.ps1
   
   # Linux/Mac
   python scripts/start_services.py
   ```

## 📋 Project Structure

```
TheRecruitmentSystem-master/
├── README.md                    # This file
├── README_PYTHON.md            # Comprehensive documentation
├── requirements.txt            # Python dependencies
├── start_all_services.ps1     # Windows startup script
├── .gitignore                 # Git ignore rules
├── database/                  # Database schemas and data
│   ├── schema.sql
│   ├── data.sql
│   └── mysql_new/
├── scripts/                   # Utility scripts
│   ├── start_services.py
│   ├── test_system.py
│   ├── test_db_connection.py
│   └── init_database.py
├── shared/                    # Shared modules
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── discovery_service/         # Service discovery
├── config_service/           # Configuration management
├── auth_service/             # Authentication & authorization
├── registration_service/     # User registration
├── job_application_service/  # Job application management
└── edge_service/             # API Gateway
```

## 🔧 Services

- **Edge Service** (Port 8080) - API Gateway with routing and authentication
- **Discovery Service** (Port 9090) - Service registration and discovery
- **Config Service** (Port 9999) - Centralized configuration management
- **Auth Service** (Port 8081) - JWT-based authentication
- **Registration Service** (Port 8888) - User registration and management
- **Job Application Service** (Port 8082) - Job application processing

## 📖 Documentation

For detailed documentation, setup instructions, API reference, and troubleshooting, see:

**[📚 README_PYTHON.md](README_PYTHON.md)**

## 🧪 Testing

```bash
# Test database connection
python scripts/test_db_connection.py

# Run system tests
python scripts/test_system.py
```

## 🔒 Security

- JWT-based authentication
- Role-based access control
- Password hashing with bcrypt
- Input validation and sanitization

## 📊 Monitoring

- Health check endpoints on all services
- Structured JSON logging
- Request/response monitoring
- Error tracking and correlation

## 🚀 Features

- ✅ Microservices architecture
- ✅ Robust error handling
- ✅ Circuit breaker pattern
- ✅ Service discovery
- ✅ API Gateway
- ✅ Database resilience
- ✅ Health monitoring
- ✅ Security best practices

---

**For complete documentation and advanced usage, see [README_PYTHON.md](README_PYTHON.md)** 