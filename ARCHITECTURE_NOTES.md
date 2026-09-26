# Design & Architecture Notes

## 1. Database Schema & Normalisation

I used PostgreSQL with three main tables: `users`, `bookings`, and `reviews`.

The `users` table stores the basic user details and their role (`admin`, `provider`, or `customer`). The `bookings` table connects a customer with a provider and stores the booking time and status. The `reviews` table is connected to a booking using `booking_id`.

I chose this structure to avoid storing the same information in multiple places. For example, I did not store `provider_id` again inside the `reviews` table because it can already be found through the booking. This keeps the database more consistent. The small tradeoff is that getting all reviews for a provider requires a JOIN between the `reviews` and `bookings` tables, but this is reasonable for this application.

## 2. RBAC Approach

I used JWT authentication along with role-based access control.

When a user logs in, they receive a JWT containing their user ID and role. The API uses this information to check what the user is allowed to access.

Admins can access all bookings. Providers can only access bookings where they are the provider, and customers can only access bookings that belong to them. I also check ownership when updating or deleting bookings.

I use the user ID from the JWT instead of trusting a `customer_id` sent by the client. This is important because a user could otherwise change the ID in the request and try to access someone else's booking.

For reviews, I also check that the user is a customer, owns the booking, the booking is completed, and a review has not already been created for that booking.

## 3. Production-Readiness Gaps

The current project is mainly focused on meeting the assessment requirements, so there are some things I would improve before using it in production.

The API should use HTTPS/TLS and rate limiting to protect against attacks such as brute-force login attempts. Secrets such as the JWT secret and database credentials should also be stored using a proper secrets manager instead of keeping them in environment files.

The Redis queue currently uses `LPUSH` and `BRPOP`. If the worker crashes after taking a job from Redis, that job could be lost. For a production system, I would use something like Redis Streams or Celery with acknowledgements and retries.

I would also add better logging, monitoring, error tracking, and metrics so that problems can be detected quickly. As the application grows, PostgreSQL connection pooling may also need to be improved using a tool such as PgBouncer.

Database changes are handled using Alembic, which allows schema changes to be tracked and applied in a controlled way.
