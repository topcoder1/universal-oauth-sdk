# Vault API

Managed OAuth token storage service with automatic refresh and webhooks.

## Features

- 🔐 Secure token storage (AES-256-GCM encryption)
- 🔄 Automatic token refresh
- 📡 Webhook notifications
- 🔑 API key authentication
- 👥 Multi-tenant isolation
- 💳 Stripe billing integration

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

## API Documentation

Once running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
vault-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API endpoints
│   │   ├── v1/
│   │   │   ├── tokens.py
│   │   │   ├── webhooks.py
│   │   │   └── auth.py
│   ├── core/                # Core functionality
│   │   ├── security.py      # Authentication
│   │   ├── encryption.py    # Token encryption
│   │   └── refresh.py       # Token refresh
│   └── tasks/               # Background tasks
│       └── refresh_tokens.py
├── alembic/                 # Database migrations
├── tests/                   # Tests
├── requirements.txt
└── .env.example
```

## Development

### Run Tests

```bash
pytest
```

### Create Migration

```bash
alembic revision --autogenerate -m "description"
```

### Run Background Worker

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment instructions.

## License

MIT
