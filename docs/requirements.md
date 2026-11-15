# Requirements - Double-Entry Ledger and Idempotent Payments API

## Purpose and Scope

In fintech companies and startups, a double-entry ledger system serves as the source of truth for both customers and the business. It provides an append-only record showing how, when, and by whom money was moved. This also serves as an audit trail for financial investigations and legal purposes.

### In Scope
1. Simulated M-Pesa/bank payments.
2. User registration and login.
3. Create deposits and withdrawals.
4. Account balance retrieval.
5. Transaction statements.
6. Transaction reversals.
7. Idempotency keys to prevent duplicate financial operations.
8. Simple frontend using HTML, CSS, JavaScript, and Django templates.

### Out of Scope
1. Real M-Pesa/bank integrations.
2. Real-time updates.
3. Fraud detection.
4. Complex frontend.

## Actors
1. Client
2. System
3. Administrator

## Functional Requirements

| ID | Requirement | Actor | Description | Priority |
|---|---|---|---|---|
| FR-01 | User Registration | Client | The system shall register new users after validating their information and securely storing their credentials. | Must |
| FR-02 | User Login | Client | The system shall authenticate registered users using their credentials and grant access to authorized resources. | Must |
| FR-03 | Deposit Funds | Client | The system shall process deposits and create corresponding debit and credit ledger entries atomically. | Must |
| FR-04 | Withdraw Funds | Client | The system shall process withdrawals after verifying sufficient funds and create balanced ledger entries. | Must |
| FR-05 | Get Account Balance | Client | The system shall retrieve and return the client's current account balance based on recorded financial transactions. | Must |
| FR-06 | Generate Account Statement | Client | The system shall retrieve and display the client's chronological transaction history, including deposits, withdrawals, and reversals. | Must |
| FR-07 | Reverse Transaction | Client / Administrator | The system shall reverse eligible transactions by creating compensating ledger entries without modifying original entries. | Must |
| FR-08 | Idempotent Transaction Processing | Client / System | The system shall prevent duplicate financial operations when identical requests are retried using the same idempotency key. | Must |

## Non-Functional Requirements

| ID | Requirement | Description | Measurable Criteria |
|---|---|---|---|
| NFR-01 | Financial Correctness | The system shall maintain double-entry accounting integrity. | Total debits must equal total credits for every posted transaction. Failed transactions must not leave partial ledger entries. |
| NFR-02 | Idempotency | The system shall prevent duplicate financial operations. | Given 10 identical requests with the same idempotency key, exactly one financial operation shall execute. Reusing a key with a different payload shall return HTTP 409. |
| NFR-03 | Concurrency | The system shall maintain financial consistency during simultaneous operations. | Given a balance of KSh 1,000, 50 concurrent withdrawal requests of KSh 800 shall result in exactly one successful withdrawal and a final balance of KSh 200. |
| NFR-04 | Durability | Successfully committed transactions shall remain permanently recorded. | Committed transactions shall remain available after application restarts. Ledger entries shall not be modified or deleted through ordinary transaction operations. |
| NFR-05 | Performance | The system shall respond within acceptable time limits under normal operating conditions. | 95% of balance retrieval requests shall complete within 500 ms. 95% of deposits and withdrawals shall complete within 1 second, excluding simulated provider delays. |
| NFR-06 | Security | The system shall protect user credentials and financial records. | Passwords shall be securely hashed. All protected endpoints shall require authentication. Users shall only access their own financial records unless authorized. |

## Constraints and Assumptions

### Constraints
1. Single geographical region (Kenya).
2. PostgreSQL as the primary database.
3. Redis for caching and message brokering.
4. Celery for background task processing.
5. Django and Django REST Framework for the backend.
6. HTML, CSS, JavaScript, and Django templates for the frontend.
7. Kenyan Shillings (KES) as the supported currency.

### Assumptions
1. Users have internet access.
2. M-Pesa and bank integrations are simulated.
3. Each client has an account maintained by the system.
4. PostgreSQL is the primary source of truth for financial records.

## Acceptance Criteria

| ID | Acceptance Criterion | Expected Result |
|---|---|---|
| AC-01 | User registration and authentication | Users can register and log in successfully using valid credentials. |
| AC-02 | Deposit processing | Successful deposits increase account balances and generate balanced ledger entries. |
| AC-03 | Withdrawal processing | Successful withdrawals reduce account balances without allowing overdrafts. |
| AC-04 | Balance retrieval | Retrieved balances accurately reflect posted ledger transactions. |
| AC-05 | Transaction statements | Clients can retrieve accurate statements containing their transaction history. |
| AC-06 | Transaction reversal | Eligible transactions can be reversed through compensating entries while preserving original ledger records. |
| AC-07 | Idempotency | Repeated requests cannot execute the same financial operation more than once. |
| AC-08 | Concurrency | Simultaneous withdrawals cannot cause account overdrafts or inconsistent balances. |
| AC-09 | Durability | Committed financial records remain available after application restarts. |
| AC-10 | Financial integrity | Every posted transaction has balanced debit and credit entries. |
| AC-11 | Security | Unauthorized users cannot access protected endpoints or other users' financial records. |
| AC-12 | Performance | The system meets the response-time targets defined in the non-functional requirements. |