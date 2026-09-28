# SDD templates

## ADR - `sdd/decisions/ADR-NNN-<slug>.md`

Statuses: `Proposed`, `Accepted`, `Rejected`, `Superseded` (by ADR-NNN).

```markdown
# ADR-001: Use PostgreSQL

## Status
Accepted

## Context
Why the decision is necessary.

## Options considered
- Option A
- Option B

## Decision
What was selected.

## Reasons
Why this option was selected over the others.

## Consequences
Positive and negative consequences.

## Related requirements
- REQ-001
- REQ-007
```

## Feature spec - section of `sdd/spec.md` or `sdd/specs/feature-NNN-<slug>.md`

Include only the sections that apply.

```markdown
# FEAT-001: <name>

Purpose:
User story:          As a <actor>, I want <goal>, so that <benefit>
Actors:
Preconditions:
Requirements:        REQ-003, REQ-004
User flow:
Business rules:
Validation:
Error cases:
Permissions:
Data changes:
API changes:
UI behavior:
External integrations:
Security considerations:
Performance considerations:
Dependencies:
Open questions:

## Acceptance criteria
(see format below)
```

## Acceptance criteria

Given/When/Then, observable behavior only. Cover important failure cases, not
just the happy path.

```text
AC-1
Given an authenticated user
When the user submits a valid order
Then the order is created
And the order receives a unique identifier
And the user can retrieve the order using that identifier

AC-2
Given an authenticated user
When the user submits an order with an out-of-stock item
Then no order is created
And the user sees which item is unavailable
```
