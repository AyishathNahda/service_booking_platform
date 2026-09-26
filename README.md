# Service Booking Platform

A full-stack REST API built with FastAPI, PostgreSQL, and Redis for booking services, leaving reviews, and processing background tasks.

## Setup & Running the Application

This application is fully containerized with Docker. You do not need to install Python locally.

1. Clone the repository.
2. Ensure Docker and Docker Compose are installed.
3. Start the application stack (API, Worker, PostgreSQL, Redis):

```bash
docker compose up --build -d
```

The API will be available at `http://localhost:8000`.

## API Usage

FastAPI automatically generates interactive Swagger documentation.
Once the application is running, navigate to:

- **Swagger UI**: `http://localhost:8000/docs`

You can test all endpoints directly from your browser. 

**Quick Start Flow:**
1. Use `POST /auth/register` to create a `provider` and a `customer`.
2. Use `POST /auth/login` to get a JWT token for your customer. Click the "Authorize" button in Swagger to inject the token.
3. Use `POST /bookings` to book a service with the provider.
4. Try to leave a review via `POST /reviews` (it will fail because the booking is pending).
5. Use `PUT /bookings/{id}` to change the status to `completed`.
6. Use `POST /reviews` to leave a review.
7. Use `POST /reviews/summarize` to trigger a background job on the Redis queue.

## Architecture

The system uses a modern, scalable, asynchronous microservice architecture:
- **FastAPI**: Provides a high-performance, asynchronous REST API.
- **PostgreSQL**: Serves as the primary relational database, chosen for its strict ACID compliance and JSONB support.
- **Redis Queue**: Acts as a message broker to offload heavy tasks.
- **Background Worker**: A separate Python container that continuously consumes jobs from Redis.

```text
Client -> FastAPI -> PostgreSQL (Data)
             |
             v
         Redis Queue -> Background Worker -> (Future LLM)
```

## Database Design

The schema is built using SQLAlchemy ORM and managed by Alembic migrations.

- **Users**: Stores `admin`, `provider`, and `customer` identities with hashed passwords (bcrypt).
- **Bookings**: Tracks service appointments. Links to exactly one Provider and one Customer.
- **Reviews**: Tracks customer feedback. Enforces a strict one-to-one relationship with a completed booking via unique constraints to prevent duplicate reviews.

## Role-Based Access Control (RBAC)

The API enforces strict RBAC at the server level using FastAPI dependencies and cryptographic identity (JWT):
- **Admins**: Can read and modify any booking.
- **Providers**: Can only read and modify bookings where `provider_id` matches their authenticated user ID.
- **Customers**: Can only read and modify bookings where `customer_id` matches their authenticated user ID.

A `404 Not Found` is thrown before a `403 Forbidden` to prevent malicious actors from guessing valid booking IDs.

## Redis Queue

The `/reviews/summarize` endpoint pushes tasks onto a Redis list using `lpush` and immediately responds to the client, preventing the API from hanging during long (e.g. 5-30s) LLM text-generation tasks.

A separate worker container runs an infinite loop using `brpop` (blocking right pop) to instantly detect and process incoming jobs without aggressively polling the database. *(Note: The current worker is intentionally a stub that sleeps for 2 seconds to simulate processing).*

## Testing

An automated testing suite is built with Pytest. It overrides the database dependency to use a lightning-fast, isolated, in-memory SQLite database (`sqlite:///:memory:`). 

To run the tests locally inside the Docker container:

```bash
docker compose exec api env PYTHONPATH=/code pytest tests/ -v
```

A GitHub Actions CI pipeline is also configured to automatically lint (Ruff) and run these tests on every push to `main`.
