# Social Media API

A scalable and secure RESTful API for a social media platform built with **FastAPI**. This project supports user registration, authentication, post creation, liking posts, and more. It is designed with modern best practices, including asynchronous database operations, token-based authentication, and robust testing.

The API is deployed and accessible on this [link](https://hrutikghaghada.tech/docs).

## Features

- **User Management**: Register and login users.
- **Post Management**: Create, update, delete, and retrieve posts.
- **Like System**: Like and unlike posts.
- **Sorting and Filtering**: Retrieve posts with sorting and search capabilities.
- **Authentication**: Secure token-based authentication using JWT.
- **Database**: PostgreSQL with SQLAlchemy for ORM and Alembic for migrations.
- **Logging**: Structured logging with obfuscation for sensitive data.
- **Testing**: Comprehensive test suite using `pytest` and `httpx`.
- **Dockerized**: Fully containerized for development and production environments.
- **CI/CD**: Automated testing, building, and deployment using GitHub Actions.

---

## Tech Stack

The project is built using the following technologies:

- **FastAPI**: For building the RESTful API.
- **PostgreSQL**: As the relational database.
- **Databases**: For asynchronous database interactions.
- **Alembic**: For database migrations.
- **JWT**: For secure token-based authentication.
- **Docker**: For containerization of the application.
- **GitHub Actions**: For CI/CD workflows.
- **pytest**: For testing the application.
- **httpx**: For making asynchronous HTTP requests in tests.
- **Pydantic**: For data validation and settings management.
- **ruff**: For linting and enforcing code quality.

---

## Project Structure

```
social_media_api/
├── alembic/                  # Database migrations
├── app/                      # Application code
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── database.py           # Database models and connection
│   ├── logging_conf.py       # Logging configuration
│   ├── main.py               # FastAPI application entry point
│   ├── models.py             # Pydantic models
│   ├── security.py           # Authentication and security utilities
│   ├── routes/               # API routes
│   │   ├── __init__.py
│   │   ├── user.py           # User-related endpoints
│   │   ├── post.py           # Post-related endpoints
│   │   ├── like.py           # Like-related endpoints
│   └── tests/                # Test suite
│       ├── __init__.py
│       ├── conftest.py       # Test fixtures
|       ├── test_security.py  # Authentication specific tests
│       ├── routes/           # Route-specific tests
│           ├── test_user.py
│           ├── test_post.py
│           ├── test_like.py
├── alembic.ini               # Alembic configuration
├── docker-compose-dev.yml    # Docker Compose for development
├── docker-compose-prod.yml   # Docker Compose for production
├── Dockerfile                # Docker configuration
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                 # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hrutikghaghada/social-media-api.git
   cd social-media-api
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Running with Docker

### Development

1. Start the development environment:
   ```bash
   docker-compose -f docker-compose-dev.yml up --build
   ```

2. Access the API at [http://localhost:8000](http://localhost:8000).

### Production

1. Build and start the production environment:
   ```bash
   docker-compose -f docker-compose-prod.yml up --build
   ```

2. Access the API at [http://localhost:8000](http://localhost:8000).

---

## Testing

Run the test suite using `pytest`:

```bash
pytest
```

---

## CI/CD

This project uses **GitHub Actions** for continuous integration and deployment. The workflow includes:

- Linting with `ruff`
- Running database migrations
- Testing with `pytest`
- Building and pushing Docker images
- Deploying to a production server

---

## Configuration

The application uses environment variables for configuration. Refer to `.env.example` for all available variables.

---

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Databases](https://github.com/encode/databases)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Docker](https://www.docker.com/)
- [GitHub Actions](https://github.com/features/actions)
