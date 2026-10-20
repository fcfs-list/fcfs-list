# FCFS-List Roadmap

This roadmap describes proposed work to turn the existing API and marketplace data model into a reliable, end-to-end first-come, first-served marketplace. It is a planning guide, not a delivery-date commitment. Priorities may change as product requirements and user feedback become clearer.

## Current baseline

The repository currently provides a FastAPI backend with PostgreSQL persistence, Auth0-protected API resources, an admin interface, product images via Google Cloud Storage, and models/endpoints for wishes, products, matches, offers, and transactions.

The API can store matches and their queue order, but it does not yet automatically discover products matching a wish, generate matches when products or wishes change, or automatically advance a queue when a buyer declines or times out. There is also no customer-facing frontend in this repository. Automated tests and CI/CD are not currently established.

## Guiding principles

- **Fairness:** define and explain exactly how queue position is earned and preserved.
- **Correctness under concurrency:** never offer the same item to multiple buyers at once or skip a qualified buyer due to a race.
- **Privacy and safety:** reveal only the information needed at each marketplace stage and provide abuse-reporting and moderation paths.
- **Observable automation:** record why a match was made, what happened to it, and why a queue advanced.
- **Incremental delivery:** validate the basic buyer/seller flow with users before adding complex ranking or payments.

## Proposed phases

### 1. Establish a dependable engineering baseline — P0

- Add a test suite organized by unit, API/integration, and end-to-end tests.
- Cover key behaviors: authentication and authorization, product and wish validation, offer/match status changes, deadline boundaries, queue ordering, duplicate prevention, and transaction invariants.
- Run integration tests against PostgreSQL (not only an in-memory substitute); use isolated test data and ensure test cleanup.
- Add test fixtures/factories and a documented local test command. Keep external services such as Auth0 and Google Cloud Storage behind test doubles or dedicated test credentials.
- Add formatting, linting, type-checking, and migration checks where practical; establish an initial coverage baseline and grow it with critical paths.
- Review existing endpoint authorization and ownership checks, error responses, pagination, and input validation; fix inconsistencies and add regression tests.

**Exit criteria:** contributors can run the checks locally and in automation; critical marketplace rules have repeatable tests; schema changes are reviewed and tested against PostgreSQL.

### 2. Specify and implement deterministic matching — P0

- Write a product decision document defining eligibility and queue policy. Specify how keywords, brands, categories, area/radius, item condition, price, size, sell-or-lend preferences, and product availability affect a match.
- Define queue entry time and tie-breaking, including what happens when a wish is edited, a user changes preferences, or a product is relisted.
- Trigger candidate matching when a product becomes eligible and when a wish is created or changed. Avoid duplicate matches and exclude the seller and ineligible/deleted users.
- Persist match provenance and relevant rule/version information so support teams can explain why a buyer was or was not considered.
- Make queue claims atomic and concurrency-safe at the database level. A product should have at most one active buyer offer/reservation at a time.
- Implement a clear state machine for waiting, offered, accepted, declined, expired, cancelled, completed, and any required terminal states. On decline or expiry, advance to the next eligible buyer according to the documented policy.
- Add deadline processing, retries, idempotency, and recovery for interrupted background work. Consider a database-backed job/outbox approach before adding an external queue service.
- Notify affected buyers and sellers when a match or offer is created, expires, or advances; begin with email or in-app notifications after preferences and privacy are defined.
- Add fairness, duplicate-event, race-condition, and failure-recovery tests, including simultaneous responses to the same item.

**Exit criteria:** a product can enter a deterministic, auditable queue from eligible wishes; only the current buyer can act; timeout/decline moves the item forward safely; the full behavior is covered by automated tests.

### 3. Complete the marketplace API and data lifecycle — P1

- Review API contracts and authorization scopes; document ownership rules and standardize status transitions and validation errors.
- Add pagination, filtering, and sorting for growing product, wish, match, offer, message, and transaction collections.
- Improve database constraints and indexes for actual query patterns; add migration rollback/recovery guidance and test upgrades from a clean database and a prior release.
- Define product lifecycle behavior for drafts, availability, expiration, sold/hidden/deleted states, and relisting; ensure related matches/offers cannot remain actionable after a product is unavailable.
- Review image handling for size/type limits, safer object naming, authorization, and cleanup of orphaned uploads.
- Add API contract examples and maintain a clear, versioned public API policy.

**Exit criteria:** core endpoints behave consistently, remain usable as data grows, and lifecycle changes cannot leave stale or invalid offers.

### 4. Build the customer-facing marketplace frontend — P1

Create a separate customer application (web first; select a framework after product requirements are agreed). Prioritize a responsive and accessible experience for:

- Sign-up, sign-in, profile, and location/preferences.
- Browsing and searching listings, with useful filters and product details.
- Creating and managing wishes and seeing queue status in plain language.
- Listing, editing, and managing products, images, and availability.
- Receiving and responding to a match/offer, including deadlines and queue advancement.
- Messaging, transaction progress, and clear completion/cancellation states.
- Reporting a listing or user, blocking where appropriate, and contacting support.

Include loading, empty, error, offline/retry, and expired states; keyboard navigation, screen-reader labels, and mobile layouts; and frontend tests for key user journeys. Keep API tokens secure and avoid exposing private buyer information before the relevant stage.

**Exit criteria:** a buyer and seller can complete the core lifecycle without Swagger or the admin interface, and usability/accessibility checks cover the primary paths.

### 5. Security, privacy, and trust — P1

- Threat-model account takeover, unauthorized object access, spam, fraudulent listings, scraping, and abuse of the matching/offer flow.
- Audit every endpoint for object-level authorization and least-privilege Auth0 scopes; add tests for cross-user access denial.
- Add rate limits and abuse controls for sign-up, messaging, listing creation, and other sensitive operations.
- Define retention, deletion, export, consent, and audit-log policies for personal data and messages.
- Add moderation workflows for reports, prohibited listings, and repeat abuse; define operational ownership and response expectations.
- Move secrets to a managed secret store in deployed environments, rotate credentials, and document incident response. Never commit credentials or production data.
- Review dependency and container vulnerabilities regularly and establish a supported Python/runtime upgrade policy.

**Exit criteria:** security-sensitive flows are tested, user data handling is documented, and abuse reports have a clear review process.

### 6. CI/CD and release management — P1

- Add pull-request CI for formatting/linting, type checks, unit tests, PostgreSQL integration tests, migration validation, and frontend checks once available.
- Build the backend container reproducibly; scan dependencies and images and publish versioned artifacts from trusted branches/tags.
- Deploy automatically to a staging environment; run smoke tests and migration checks before promotion.
- Use explicit approvals or protected environments for production, with health checks, rollback procedures, and backward-compatible database migration practices.
- Keep development, staging, and production configuration separate; verify required environment variables at startup and avoid insecure defaults.
- Document versioning, changelog/release notes, and how to roll forward or roll back an application release.

**Exit criteria:** a change can be validated and deployed repeatably to staging, and production promotion/rollback has a documented owner and procedure.

### 7. Reliability, observability, and operations — P2

- Add structured logs with request/correlation IDs and useful audit events, while excluding tokens and sensitive personal information.
- Add health/readiness checks, error reporting, metrics, and alerts for API failures, database availability, job backlog, and match/notification failures.
- Define service-level targets and dashboards for API latency/errors and marketplace outcomes such as time-to-first-offer and queue completion.
- Test backup restoration and document database recovery, data migrations, incident response, and on-call/support procedures.
- Add performance/load tests for product browsing, candidate matching, queue advancement, and concurrent offer responses.
- Establish cost and quota monitoring for PostgreSQL, image storage, email/notification providers, and any background-processing service.

**Exit criteria:** operators can detect failures, trace a match through its lifecycle, restore data, and understand whether service and marketplace health are degrading.

### 8. Learn and iterate — P2

- Run a small pilot with representative buyers and sellers and gather qualitative feedback.
- Measure conversion and fairness without collecting unnecessary personal data; review whether the queue policy produces the intended outcomes.
- Improve search relevance, notifications, localization, and seller tools based on evidence.
- Consider payments, shipping, lending deposits/returns, recommendations, or native mobile clients only after the core exchange model and operational requirements are validated.

**Exit criteria:** feature investments are informed by user feedback and agreed marketplace metrics rather than assumptions.

## Suggested order

1. Engineering baseline and written queue policy.
2. Automatic matching, safe queue progression, and integration tests.
3. API lifecycle, security/privacy, and staging CI/CD.
4. Customer frontend for the complete buyer/seller journey.
5. Production operations, pilot, and evidence-driven improvements.

## How to use this roadmap

Treat the phases as a dependency-aware backlog. Break a phase into small issues with acceptance criteria, identify product decisions before implementation, and update this document when priorities or requirements change. Do not interpret phase labels as release dates.
