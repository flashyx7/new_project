# Recruitment System - Python Microservices

A robust, production-ready microservices architecture for recruitment management built with Python, FastAPI, and modern DevOps practices.

## 🚀 Features

- **Microservices Architecture**: 6 independent services with clear separation of concerns
- **Robust Error Handling**: Comprehensive error handling with proper HTTP status codes
- **Structured Logging**: JSON-structured logging with correlation IDs
- **Circuit Breaker Pattern**: Automatic service failure detection and recovery
- **Service Discovery**: Dynamic service registration and discovery
- **API Gateway**: Centralized routing with authentication and rate limiting
- **Database Resilience**: Connection pooling and retry logic
- **Health Monitoring**: Built-in health checks for all services
- **Security**: JWT-based authentication with role-based access control

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Service  │    │  Discovery      │    │   Config        │
│   (API Gateway) │    │  Service        │    │   Service       │
│   Port: 8080    │    │  Port: 9090     │    │  Port: 9999     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Auth Service  │    │  Registration   │    │  Job Application│
│   Port: 8081    │    │  Service        │    │  Service        │
└─────────────────┘    │  Port: 8888     │    │  Port: 8082     │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                └───────────────────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │   MySQL         │
                                │   Database      │
                                │   Port: 3307    │
                                └─────────────────┘
```

## 📋 Services

### 1. Edge Service (API Gateway)
- **Port**: 8080
- **Purpose**: Centralized routing, authentication, rate limiting
- **Features**: Circuit breaker, request logging, CORS handling

### 2. Discovery Service
- **Port**: 9090
- **Purpose**: Service registration and discovery
- **Features**: Consul integration, health monitoring

### 3. Config Service
- **Port**: 9999
- **Purpose**: Centralized configuration management
- **Features**: Environment-specific configs, hot reloading

### 4. Auth Service
- **Port**: 8081
- **Purpose**: Authentication and authorization
- **Features**: JWT tokens, password hashing, role validation

### 5. Registration Service
- **Port**: 8888
- **Purpose**: User registration and management
- **Features**: User validation, duplicate prevention

### 6. Job Application Service
- **Port**: 8082
- **Purpose**: Job application management
- **Features**: Application tracking, status management

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Consul (optional, for service discovery)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TheRecruitmentSystem-master
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Start MySQL and create database
   python init_database.py
   ```

4. **Start all services**
   ```bash
   # Windows
   .\start_all_services.ps1
   
   # Linux/Mac
   python start_services.py
   ```

### Manual Setup

1. **Environment Variables**
   ```bash
   export DB_HOST=localhost
   export DB_PORT=3307
   export DB_USER=recruitment_user
   export DB_PASSWORD=recruitment_pass
   export DB_NAME=recruitment_system
   export JWT_SECRET_KEY=your-secret-key-here
   ```

2. **Start services individually**
   ```bash
   # Terminal 1: Discovery Service
   python discovery_service/main.py
   
   # Terminal 2: Config Service
   python config_service/main.py
   
   # Terminal 3: Auth Service
   python auth_service/main.py
   
   # Terminal 4: Registration Service
   python registration_service/main.py
   
   # Terminal 5: Job Application Service
   python job_application_service/main.py
   
   # Terminal 6: Edge Service
   python edge_service/main.py
   ```

## 🔧 Error Handling & Debugging

### Error Handling Features

- **Structured Logging**: All errors are logged with context and correlation IDs
- **Proper HTTP Status Codes**: 400, 401, 403, 404, 409, 500, 503, 504
- **Circuit Breaker**: Automatic service failure detection
- **Graceful Degradation**: Services continue working even if dependencies fail
- **Detailed Error Messages**: Development-friendly error details

### Debugging Tools

1. **Health Checks**
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:9090/health
   curl http://localhost:9999/health
   curl http://localhost:8081/health
   curl http://localhost:8888/health
   curl http://localhost:8082/health
   ```

2. **System Tests**
   ```bash
   python test_system.py
   ```

3. **Database Connection Test**
   ```bash
   python test_db_connection.py
   ```

4. **Log Analysis**
   ```bash
   # All services use structured JSON logging
   # Check logs for correlation IDs and error context
   ```

### Common Issues & Solutions

#### 1. Port Already in Use
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8080
kill -9 <PID>
```

#### 2. Database Connection Issues
```bash
# Test database connection
python test_db_connection.py

# Check MySQL status
sudo systemctl status mysql
```

#### 3. Service Discovery Issues
```bash
# Check Consul
curl http://localhost:8500/v1/status/leader

# Check service registration
curl http://localhost:9090/services
```

## 🔒 Security

### Authentication Flow

1. **User Registration**
   ```bash
   POST /registration/register
   {
     "username": "user@example.com",
     "password": "secure_password",
     "firstname": "John",
     "lastname": "Doe",
     "email": "john@example.com"
   }
   ```

2. **User Login**
   ```bash
   POST /auth/login
   {
     "username": "user@example.com",
     "password": "secure_password"
   }
   ```

3. **API Access**
   ```bash
   # Include JWT token in Authorization header
   Authorization: Bearer <jwt_token>
   ```

### Role-Based Access Control

- **Applicant**: Can register, login, submit applications
- **Recruiter**: Can view applications, change statuses
- **Service**: Internal service-to-service communication

## 📊 Monitoring & Observability

### Health Monitoring
- All services expose `/health` endpoints
- Automatic health checks every 30 seconds
- Service status tracking

### Logging
- Structured JSON logging
- Correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARNING, ERROR

### Metrics
- Request/response times
- Error rates
- Service availability

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
python test_system.py

# Test specific service
python -m pytest tests/test_auth_service.py
```

### Manual Testing
```bash
# Test user flow
curl -X POST http://localhost:8080/registration/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","firstname":"Test","lastname":"User","email":"test@example.com"}'

curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Considerations

1. **Environment Variables**
   - Set production database credentials
   - Use strong JWT secret keys
   - Configure proper CORS origins

2. **Security**
   - Enable HTTPS
   - Use production-grade database
   - Implement rate limiting

3. **Monitoring**
   - Set up log aggregation
   - Configure alerting
   - Monitor service health

## 📝 API Documentation

### Edge Service (API Gateway)
- **Base URL**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/docs

### Service Endpoints

#### Auth Service
- `POST /auth/login` - User authentication
- `GET /auth/validate` - Token validation

#### Registration Service
- `POST /registration/register` - User registration
- `GET /registration/{lang}/persons/{user_id}` - Get user details

#### Job Application Service
- `POST /jobapplications` - Submit application
- `GET /jobapplications/{application_id}` - Get application
- `PUT /jobapplications/status/{application_id}` - Update status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Open an issue with detailed information

---

**Note**: This system has been thoroughly debugged and optimized for production use with comprehensive error handling, logging, and monitoring capabilities. 