# ADR 0001: Store idempotency keys in Postgres, inside the transfer transaction

- **Status:** Accepted
- **Date:** 2026-11-15
- **Satisfies:** FR-2 (transfer), NFR-1 (ledger sums to zero), NFR-3 (retry creates exactly one transaction)

## Context

Clients call `POST /transfers` over unreliable mobile networks. A request can
succeed on the server while the response is lost. The client times out and
retries, and without protection the retry moves the money a second time.

We need a rule that makes a retry with the same `Idempotency-Key` return the
original result and create no second transaction. This must hold even when:

1. The server crashes mid-request.
2. Two requests with the same key arrive at the same moment.
3. The same key is reused with a different body (a client bug).

## Decision

Store idempotency keys in a Postgres table, written **in the same database
transaction** as the transfer, with a **unique constraint** on the key.

Request flow inside the ledger module:

1. `BEGIN`
2. `INSERT` the key (unique constraint rejects duplicates)
3. Lock accounts with `SELECT ... FOR UPDATE`, in sorted ID order
4. Check balance, write transaction and entries, update cached balances
5. Save the response on the key row
6. `COMMIT`

On a unique violation, roll back, read the saved response, compare
`request_hash`, then:

- Hash matches: return the saved response.
- Hash differs: return `409 Conflict` (key reused with a different request).

## Alternatives considered

| Option | Why rejected |
|---|---|
| **Redis for keys** | Two systems can disagree. If the transfer commits and the server crashes before the Redis write, a retry finds no key and double-charges. If the key is written first and the transfer fails, a retry is blocked from a transfer that never happened. |
| **Check-then-insert in app code** | Race condition. Two simultaneous retries both see "no key" and both proceed. Only a DB constraint closes this. |

## Consequences

**Positive**
- Key and transfer commit together or not at all. A crash at any point leaves a consistent state.
- Concurrent retries are coordinated by Postgres: the second insert blocks until the first transaction commits (retry then gets the saved response) or rolls back (retry proceeds normally). No "in progress" state is needed.
- One system holds all the state, which keeps correctness easy to reason about and test.

**Negative**
- Every transfer pays one extra insert, and the keys table grows. Mitigation: a cleanup job expires keys after 24 to 48 hours.
- A blocked duplicate holds a DB connection while it waits. Mitigation: a lock timeout, returning 409 or 503 if exceeded.
- Throughput is bounded by a single Postgres. Acceptable at our assumed scale. Revisit if writes exceed several hundred per second.

## Verification

- Test: send the same request with the same key 20 times concurrently, then assert exactly one transaction exists and all responses are identical.
- Test: same key with a different amount returns 409.
- Test: simulate a crash after the transfer writes but before commit, then assert no transaction and no key row remain.