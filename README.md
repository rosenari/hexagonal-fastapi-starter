# Hexagonal FastAPI Starter

A production-ready FastAPI application built with **Hexagonal Architecture** (Ports and Adapters pattern), featuring comprehensive user management, robust logging, dependency injection, and Docker support.

## 🏗️ Architecture

This project follows **Hexagonal Architecture** principles with clear separation of concerns:

```
app/
├── domain/          # Business logic & entities
├── application/     # Use cases & DTOs
├── infrastructure/  # External adapters (DB, logging, etc.)
└── presentation/    # API controllers & middleware
```

## 🚀 Features

- ✅ **Hexagonal Architecture** with clean separation of concerns
- ✅ **FastAPI** with automatic OpenAPI documentation
- ✅ **User Management API** (CRUD operations)
- ✅ **Dependency Injection** using dependency-injector
- ✅ **SQLAlchemy** with async support (SQLite/PostgreSQL)
- ✅ **Password Security** with bcrypt hashing
- ✅ **Structured JSON Logging** with request ID propagation
- ✅ **Comprehensive Testing** with pytest (116+ tests)
- ✅ **Docker & Docker Compose** support
- ✅ **Database Migrations** support
- ✅ **CORS & Security Middleware**
- ✅ **Request/Response validation** with Pydantic v2
- ✅ **Environment Configuration** management

## 🛠️ Quick Start

### Option 1: Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd hexagonal-fastapi-starter

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Run the application
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
```

### Option 2: Docker Development

```bash
# Clone the repository
git clone <your-repo-url>
cd hexagonal-fastapi-starter

# Start with Docker Compose
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

## 🐳 Docker Configuration

### Services

- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **nginx**: Reverse proxy (port 80) - production profile

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start only app and database
docker-compose up app db

# Run with production nginx
docker-compose --profile production up

# Run tests in Docker
docker-compose run --rm app uv run pytest

# Access database
docker-compose exec db psql -U postgres -d hexagonal_fastapi

# View logs
docker-compose logs -f app
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Endpoints

- `GET /health` - Health check
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user by ID
- `GET /api/users` - List users (with pagination)

### Example API Usage

```bash
# Health check
curl http://localhost:8000/health

# Create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePassword123!"}'

# Get user
curl http://localhost:8000/api/users/{user-id}

# List users
curl "http://localhost:8000/api/users?limit=10&offset=0"
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and adjust:

```bash
# Application Settings
ENVIRONMENT=development
DEBUG=true

# Database (choose one)
DATABASE_URL=sqlite+aiosqlite:///./hexagonal_fastapi.db              # SQLite
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hexagonal_fastapi  # PostgreSQL

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Password Requirements

Passwords must contain:
- At least 8 characters
- One uppercase letter
- One lowercase letter  
- One digit
- One special character (!@#$%^&*(),.?\":{}|<>)

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/unit/presentation/api/test_users.py

# Run tests in Docker
docker-compose run --rm app uv run pytest
```

## 📁 Project Structure

```
hexagonal-fastapi-starter/
├── app/
│   ├── domain/              # Domain layer
│   │   ├── entities/        # Business entities
│   │   ├── value_objects/   # Value objects
│   │   ├── services/        # Domain services
│   │   └── exceptions.py    # Domain exceptions
│   ├── application/         # Application layer
│   │   ├── use_cases/       # Business use cases
│   │   ├── ports/           # Interfaces/Contracts
│   │   ├── dtos/            # Data transfer objects
│   │   └── exceptions.py    # Application exceptions
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── database/        # Database adapters
│   │   ├── logging.py       # Logging configuration
│   │   ├── config.py        # Settings management
│   │   └── container.py     # Dependency injection
│   ├── presentation/        # Presentation layer
│   │   └── api/             # REST API endpoints
│   └── main.py              # FastAPI app factory
├── tests/                   # Test suite
├── docker/                  # Docker configurations
├── Dockerfile              # Application container
├── docker-compose.yml      # Multi-service setup
└── pyproject.toml          # Python project config
```

## 🔄 Development Workflow

### Adding New Features

1. **Write Tests First** (TDD approach)
2. **Domain Layer**: Add entities, value objects, services
3. **Application Layer**: Create use cases and DTOs
4. **Infrastructure Layer**: Implement adapters/repositories
5. **Presentation Layer**: Add API endpoints
6. **Integration**: Wire dependencies in container

### Database Migrations

```bash
# Create migration (when you add this feature)
uv run alembic revision --autogenerate -m "Add new table"

# Apply migrations
uv run alembic upgrade head

# In Docker
docker-compose exec app uv run alembic upgrade head
```

## 🚀 Production Deployment

### Using Docker Compose with Production Profile

```bash
# Production setup with nginx
docker-compose --profile production up -d

# Environment variables for production
export DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/db"
export SECRET_KEY="your-production-secret-key"
export ENVIRONMENT="production"
export DEBUG="false"
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (coming soon).

## 🧰 Built With

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit
- **[Pydantic](https://pydantic.dev/)** - Data validation using Python type hints
- **[dependency-injector](https://python-dependency-injector.ets-labs.org/)** - Dependency injection framework
- **[pytest](https://pytest.org/)** - Testing framework
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[Docker](https://www.docker.com/)** - Containerization platform

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

If you have questions or need help, please open an issue on GitHub.
