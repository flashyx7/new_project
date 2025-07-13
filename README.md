# The Recruitment System - Python Microservices

A modern, scalable recruitment system built with Python FastAPI microservices architecture, featuring user registration, authentication, job applications, and a beautiful Bootstrap 5 frontend.

## 🚀 Features

- **Microservices Architecture**: Modular design with separate services for different functionalities
- **User Management**: Registration, authentication, and role-based access control
- **Job Applications**: Complete job application workflow with status tracking
- **Service Discovery**: Automatic service registration and discovery using Consul
- **API Gateway**: Edge service for routing and load balancing
- **Modern Frontend**: Responsive Bootstrap 5 interface with JavaScript interactivity
- **Windows Compatible**: Fully tested and optimized for Windows environments
- **Docker Support**: Containerized deployment with Docker and Docker Compose

## 🏗️ Architecture

The system consists of the following microservices:

- **Discovery Service** (Port 9090): Service registration and discovery
- **Config Service** (Port 9999): Centralized configuration management
- **Auth Service** (Port 8081): User authentication and JWT token management
- **Registration Service** (Port 8888): User registration and profile management
- **Job Application Service** (Port 8082): Job application processing and management
- **Edge Service** (Port 8080): API gateway and frontend serving

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, Pydantic
- **Database**: MySQL with PyMySQL driver
- **Authentication**: JWT tokens with passlib
- **Service Discovery**: Consul
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, integration tests

## 📋 Prerequisites

- Python 3.11 or higher
- MySQL Server
- Consul (for service discovery)
- Git
- Docker (optional, for containerized deployment)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd TheRecruitmentSystem-master
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

1. Create a MySQL database named `recruitment_system`
2. Run the database initialization script:
   ```bash
   python scripts/init_database.py
   ```

### 4. Start Consul

Download and start Consul for service discovery:
```bash
# Download Consul (Windows)
# Visit: https://www.consul.io/downloads
# Extract and run: consul agent -dev
```

### 5. Start Services

Start all services in the correct order:

```bash
# Terminal 1: Discovery Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m discovery_service.main

# Terminal 2: Config Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m config_service.main

# Terminal 3: Auth Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m auth_service.main

# Terminal 4: Registration Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m registration_service.main

# Terminal 5: Job Application Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m job_application_service.main

# Terminal 6: Edge Service
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m edge_service.main
```

### 6. Access the Application

- **Frontend**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Consul UI**: http://localhost:8500

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Individual Docker Containers

```bash
# Build images
docker build -t discovery-service ./discovery_service
docker build -t config-service ./config_service
docker build -t auth-service ./auth_service
docker build -t registration-service ./registration_service
docker build -t job-application-service ./job_application_service
docker build -t edge-service ./edge_service

# Run containers
docker run -p 9090:9090 discovery-service
docker run -p 9999:9999 config-service
docker run -p 8081:8081 auth-service
docker run -p 8888:8888 registration-service
docker run -p 8082:8082 job-application-service
docker run -p 8080:8080 edge-service
```

## 🧪 Testing

### Run Integration Tests

```bash
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m pytest tests/integration/ -v
```

### Run Unit Tests

```bash
$env:PYTHONPATH = "D:\path\to\TheRecruitmentSystem-master"; python -m pytest tests/unit/ -v
```

## 📁 Project Structure

```
TheRecruitmentSystem-master/
├── discovery_service/          # Service discovery and registration
├── config_service/            # Configuration management
├── auth_service/              # Authentication and authorization
├── registration_service/      # User registration and profiles
├── job_application_service/   # Job application processing
├── edge_service/              # API gateway and frontend
├── shared/                    # Shared modules and utilities
├── tests/                     # Test suites
├── scripts/                   # Utility scripts
├── docs/                      # Documentation
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=recruitment_system
DB_USER=your_username
DB_PASSWORD=your_password

# Service Discovery
CONSUL_HOST=localhost
CONSUL_PORT=8500
DISCOVERY_SERVICE_URL=http://localhost:9090

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Service Ports
DISCOVERY_SERVICE_PORT=9090
CONFIG_SERVICE_PORT=9999
AUTH_SERVICE_PORT=8081
REGISTRATION_SERVICE_PORT=8888
JOB_APPLICATION_SERVICE_PORT=8082
EDGE_SERVICE_PORT=8080
```

## 🔐 Security Features

- JWT-based authentication
- Password hashing with PBKDF2
- Role-based access control
- Input validation with Pydantic
- CORS protection
- Rate limiting (configurable)

## 📊 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/validate` - Token validation

### Registration
- `POST /register` - User registration
- `GET /en/persons/{id}` - Get user profile

### Job Applications
- `GET /en/competences` - Get competences
- `GET /en/statuses` - Get application statuses
- `POST /en/applications` - Submit job application
- `GET /en/applications` - List applications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for Windows-specific setup instructions
2. Review the logs in each service terminal
3. Ensure all prerequisites are installed and running
4. Verify database connectivity and Consul service discovery

## 🎯 Roadmap

- [ ] Kubernetes deployment support
- [ ] GraphQL API
- [ ] Real-time notifications
- [ ] Advanced search and filtering
- [ ] Multi-language support
- [ ] Mobile application
- [ ] Analytics dashboard
- [ ] Email notifications
- [ ] File upload support
- [ ] Advanced reporting

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Bootstrap for the beautiful UI components
- Consul for service discovery
- The original Java microservices team for the architecture inspiration
