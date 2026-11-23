
# Airport Management API

Airport Management API is a RESTful API built with Django and Django REST Framework for managing airports, routes, airplanes, flights, crews, orders, and tickets.

## Features

- Airport and route management
- Airplane and airplane type management
- Flight scheduling and crew assignment
- Flight filtering by source, destination, and departure date
- Ticket booking with seat validation
- Protection against duplicate seat bookings
- User-specific orders and tickets
- JWT authentication
- Role-based permissions
- Swagger and ReDoc API documentation
- Automated API tests
- Docker and PostgreSQL support

## Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- SQLite
- Simple JWT
- drf-spectacular
- Docker
- Docker Compose

## Installation with Docker

### 1. Clone the repository

```bash
git clone https://github.com/oleksijgrabovij/airport-management-api.git
cd airport-management-api
```

### 2. Configure environment variables

Create a `.env` file using `.env.example` as a template.

Set your own values for:

- DJANGO_SECRET_KEY
- DJANGO_DEBUG
- DJANGO_ALLOWED_HOSTS
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD

### 3. Start Docker containers

```bash
docker compose up --build
```

Database migrations are applied automatically.

### 4. Create a superuser

Open another terminal:

```bash
docker compose exec app python manage.py createsuperuser
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| /api/airport/airports/ | Manage airports |
| /api/airport/routes/ | Manage routes |
| /api/airport/airplane-types/ | Manage airplane types |
| /api/airport/airplanes/ | Manage airplanes |
| /api/airport/crews/ | Manage crews |
| /api/airport/flights/ | Manage flights |
| /api/airport/orders/ | Manage orders |
| /api/airport/tickets/ | Manage tickets |
| /api/token/ | Obtain JWT tokens |
| /api/token/refresh/ | Refresh JWT access token |

## Flight Filtering

Flights can be filtered using query parameters.

Filter by departure airport:

```http
GET /api/airport/flights/?source=1
```

Filter by destination airport:

```http
GET /api/airport/flights/?destination=2
```

Filter by departure date:

```http
GET /api/airport/flights/?departure_date=2026-12-10
```

Combine filters:

```http
GET /api/airport/flights/?source=1&destination=2&departure_date=2026-12-10
```

## Authentication

JWT authentication is supported.

Obtain access and refresh tokens:

```http
POST /api/token/
```

Request body:

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

Use the access token for authenticated requests:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Permissions

- Anonymous users can view airport and flight information.
- Staff users can create, update, and delete airport management data.
- Authenticated users can manage their own orders and tickets.
- Users cannot access another user's orders or tickets.

## API Documentation

Swagger UI:

http://localhost:8000/api/docs/

ReDoc:

http://localhost:8000/api/redoc/

OpenAPI Schema:

http://localhost:8000/api/schema/

## Running Tests

Run tests locally:

```bash
python manage.py test airport
```

Run tests with Docker:

```bash
docker compose exec app python manage.py test airport
```

## Local Development

Create and activate a virtual environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Without PostgreSQL environment variables, the project uses SQLite.

## Database

The project supports:

- SQLite for local development
- PostgreSQL when running with Docker

Docker Compose uses a persistent volume for PostgreSQL data.

## Project Status

REST API implementation with authentication, filtering,
ticket booking, API documentation, automated tests,
and Docker configuration.
