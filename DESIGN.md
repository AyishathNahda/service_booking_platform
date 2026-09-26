# Design & Architecture Notes

## 1. Schema Shape & 2. Normalisation Tradeoffs
The database schema follows strict Third Normal Form (3NF). The `users` table holds the core identity, while `bookings` act as the relational bridge between a provider and a customer. `reviews` explicitly reference `bookings` rather than floating independently. 

By tying the review directly to the booking ID, we prevent edge cases where a user might attempt to review a provider they never hired, or review the same job multiple times. The tradeoff here is a slight performance cost: fetching all reviews for a provider requires a SQL `JOIN` on the bookings table (since `provider_id` isn't duplicated into the `reviews` table). This is a textbook normalisation tradeoff (saving storage and preventing data anomalies at the cost of read query complexity), which is highly favorable for our transactional use case.

## 3. Extending RBAC (Adding a Fourth Role)
If we needed to add an `auditor` role (read-only access to everything), we would update `RoleEnum` in the SQLAlchemy models. Then, in `app/routers/bookings.py`, we would simply add one line to the `check_booking_ownership` function:
`if current_user.role == RoleEnum.auditor: return`
The same logic would be mirrored in the list endpoint queries to allow `auditor` to fetch without filters.

## 4. RBAC for Nested Organisations
Handling nested organisations (e.g., a Clinic containing multiple Providers) requires abandoning the simple "ID matches ID" checks. We would need to implement Hierarchical RBAC or Attribute-Based Access Control (ABAC). The schema would require a new `organizations` table, and users would have an `organization_id`. The authorization query would change to: "Does this user belong to an organisation that is a parent of the organisation that owns this booking?". This usually involves recursive SQL queries (CTEs) or flattening the hierarchy into path strings.

## 5. What is Missing for Production Safety
* **Rate Limiting:** The API is highly vulnerable to brute force and DDoS attacks.
* **HTTPS/TLS:** Traffic is currently unencrypted.
* **Input Sanitization:** While Pydantic handles type coercion, it doesn't heavily sanitize text (e.g., stripping HTML out of review comments to prevent XSS).
* **Logging/Observability:** We need structured JSON logging and a tool like Sentry or Datadog to track production exceptions.

## 6. Migration Strategy
We use Alembic for migrations. In production, migrations should *never* be applied automatically on application startup. Instead, the CI/CD pipeline should run `alembic upgrade head` in an isolated step *before* deploying the new code containers. For zero-downtime, schema changes must be strictly additive (e.g., add a column in V1, start writing to it in V2, drop the old column in V3).

## 7. Secrets Handling
Currently, `JWT_SECRET` and `DATABASE_URL` are managed via `.env` and Docker environment variables. In a true production environment, these should be injected dynamically at runtime using a secure vault like AWS Secrets Manager, HashiCorp Vault, or GitHub Secrets, rather than sitting in plaintext on the server disk.

## 8. Other Production Concerns
* **Redis Reliability:** Our simple `brpop` loop is fragile. If the worker crashes mid-process, the job is permanently lost. We should upgrade to Redis Streams or Celery to support dead-letter queues, acknowledgements, and automatic retries.
* **Database Connection Pooling:** SQLAlchemy is currently handling connections, but at scale, we would need an external pooler like PgBouncer to prevent connection exhaustion.
