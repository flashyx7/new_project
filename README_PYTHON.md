# The Recruitment System - Python Version

A recruitment system implemented using **Microservices architecture** with Python and FastAPI. This is a complete conversion of the original Java Spring Boot project to Python while preserving all functionalities.

## Architecture Overview

The system consists of the following microservices:

1. **Discovery Service** (Port 9090) - Service discovery and registration using Consul
2. **Config Service** (Port 9999) - Configuration management for all services
3. **Auth Service** (Port 8081) - Authentication and JWT token management
4. **Registration Service** (Port 8888) - User registration and management
5. **Job Application Service** (Port 8082) - Job application processing and management
6. **Edge Service** (Port 8080) - API Gateway and request routing

## Technology Stack

### Core Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI applications
- **Pydantic** - Data validation and settings management

### Database
- **SQLAlchemy** - SQL toolkit and ORM
- **MySQL** - Primary database
- **Alembic** - Database migration tool

### Authentication & Security
- **Python-Jose** - JWT token handling
- **Passlib** - Password hashing with bcrypt
- **HTTPBearer** - Token-based authentication

### Service Discovery & Configuration
- **Consul** - Service discovery and key-value store
- **HTTPX** - Async HTTP client for service communication

### Logging & Monitoring
- **Structlog** - Structured logging
- **JSON logging** - Machine-readable log format

### Development & Testing
- **Pytest** - Testing framework
- **Black** - Code formatting
- **Isort** - Import sorting
- **Flake8** - Linting

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker Compose

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd TheRecruitmentSystem-master
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f [service-name]
   ```

### Service URLs

- **Edge Service (API Gateway):** http://localhost:8080
- **Discovery Service:** http://localhost:9090
- **Config Service:** http://localhost:9999
- **Auth Service:** http://localhost:8081
- **Registration Service:** http://localhost:8888
- **Job Application Service:** http://localhost:8082
- **Consul UI:** http://localhost:8500
- **MySQL Database:** localhost:3306

## API Documentation

### Authentication Flow

1. **Register a new user:**
   ```bash
   POST http://localhost:8080/registration/register
   Content-Type: application/json
   
   {
     "firstname": "John",
     "lastname": "Doe",
     "date_of_birth": "1990-01-01",
     "email": "john.doe@example.com",
     "username": "johndoe",
     "password": "password123"
   }
   ```

2. **Login to get JWT token:**
   ```bash
   POST http://localhost:8080/auth/login
   Content-Type: application/json
   
   {
     "username": "johndoe",
     "password": "password123"
   }
   ```

3. **Use token for authenticated requests:**
   ```bash
   GET http://localhost:8080/jobapplications/en/competences
   Authorization: Bearer <your-jwt-token>
   ```

### Job Application Management

#### Create a job application (Applicant role required):
```bash
POST http://localhost:8080/jobapplications/en/jobapplications
Authorization: Bearer <applicant-token>
Content-Type: application/json

{
  "person_id": 1,
  "availability": {
    "from_date": "2024-01-01",
    "to_date": "2024-12-31"
  },
  "competences": [
    {
      "competence_id": 1,
      "years_of_experience": 5.0
    }
  ]
}
```

#### Get applications (Recruiter role required):
```bash
GET http://localhost:8080/jobapplications/en/jobapplications/1
Authorization: Bearer <recruiter-token>
```

#### Change application status (Recruiter role required):
```bash
PUT http://localhost:8080/jobapplications/en/jobapplications/status/1
Authorization: Bearer <recruiter-token>
Content-Type: application/json

{
  "status_id": 2
}
```

## Database Schema

The system uses the following main tables:

- **person** - User information
- **credential** - User authentication credentials
- **role** - User roles (Recruiter, Applicant, Admin)
- **application** - Job applications
- **availability** - Application availability periods
- **competence** - Available competences
- **competence_profile** - Competences for each application
- **status** - Application statuses (Pending, Accepted, Rejected)

## Service Communication

### Service Discovery
- Services register themselves with the Discovery Service on startup
- The Edge Service uses service discovery to route requests
- Consul provides health checking and service catalog

### Configuration Management
- Config Service stores configuration for all services
- Services fetch their configuration from the Config Service
- Configuration is stored in Consul key-value store

### Authentication Flow
1. User authenticates with Auth Service
2. Auth Service validates credentials and returns JWT token
3. Other services validate JWT tokens for protected endpoints
4. Service-to-service communication uses SERVICE role tokens

## Development

### Local Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database:**
   ```bash
   # Start MySQL container
   docker run -d --name mysql \
     -e MYSQL_ROOT_PASSWORD=rootpassword \
     -e MYSQL_DATABASE=recruitment_system \
     -e MYSQL_USER=recruitment_user \
     -e MYSQL_PASSWORD=recruitment_pass \
     -p 3306:3306 \
     mysql:8.0
   
   # Initialize database
   mysql -h localhost -P 3306 -u recruitment_user -p recruitment_system < docs/db/mysql/schema.sql
   mysql -h localhost -P 3306 -u recruitment_user -p recruitment_system < docs/db/mysql/data.sql
   ```

3. **Start Consul:**
   ```bash
   docker run -d --name consul \
     -p 8500:8500 \
     consul:1.15 agent -server -bootstrap-expect=1 -ui -client=0.0.0.0
   ```

4. **Run services individually:**
   ```bash
   # Start discovery service
   cd discovery_service && python main.py
   
   # Start config service
   cd config_service && python main.py
   
   # Start auth service
   cd auth_service && python main.py
   
   # Start registration service
   cd registration_service && python main.py
   
   # Start job application service
   cd job_application_service && python main.py
   
   # Start edge service
   cd edge_service && python main.py
   ```

### Testing

```bash
# Run tests for all services
pytest

# Run tests for specific service
pytest auth_service/tests/
pytest registration_service/tests/
pytest job_application_service/tests/
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8
```

## Deployment

### Production Considerations

1. **Security:**
   - Change default JWT secret keys
   - Use environment variables for sensitive data
   - Enable HTTPS/TLS
   - Implement rate limiting

2. **Database:**
   - Use production MySQL instance
   - Set up database backups
   - Configure connection pooling

3. **Monitoring:**
   - Set up application monitoring (Prometheus, Grafana)
   - Configure log aggregation
   - Set up alerting

4. **Scaling:**
   - Use load balancers
   - Implement horizontal scaling
   - Set up auto-scaling policies

### Environment Variables

```bash
# Database
DATABASE_URL=mysql://user:password@host:port/database

# JWT
JWT_SECRET_KEY=your-secret-key-here

# Consul
CONSUL_HOST=consul-host
CONSUL_PORT=8500

# Service URLs
DISCOVERY_SERVICE_URL=http://discovery-service:9090
CONFIG_SERVICE_URL=http://config-service:9999
```

## Migration from Java Version

### Key Changes

1. **Framework:** Spring Boot → FastAPI
2. **Service Discovery:** Netflix Eureka → Consul
3. **Configuration:** Spring Cloud Config → Custom Config Service
4. **API Gateway:** Netflix Zuul → Custom Edge Service
5. **Authentication:** Spring Security → Custom JWT implementation
6. **Database:** JPA/Hibernate → SQLAlchemy
7. **Testing:** JUnit → Pytest

### Preserved Functionality

- All API endpoints and business logic
- Database schema and relationships
- Authentication and authorization flows
- Service communication patterns
- Error handling and validation
- Logging and monitoring

## Troubleshooting

### Common Issues

1. **Service not starting:**
   - Check Docker logs: `docker-compose logs [service-name]`
   - Verify database connection
   - Check Consul connectivity

2. **Authentication failures:**
   - Verify JWT token format
   - Check token expiration
   - Validate user credentials

3. **Database connection issues:**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database schema is initialized

4. **Service discovery issues:**
   - Check Consul health status
   - Verify service registration
   - Check network connectivity

### Logs

All services use structured JSON logging. Logs can be viewed with:

```bash
# Docker logs
docker-compose logs -f

# Service-specific logs
docker-compose logs -f auth-service
docker-compose logs -f registration-service
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run code quality checks
6. Submit a pull request

## License

This project is licensed under the same terms as the original Java version.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review service logs
3. Open an issue on GitHub
4. Contact the development team 