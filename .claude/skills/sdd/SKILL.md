---
name: sdd
description: Drives a software project through Specification-Driven Development (SDD) - discovery interview, requirements, architecture with ADRs, feature specs, readiness checks, then task-by-task implementation against the accepted spec. Use when starting a new project or a large feature, when the user says "plan this project", "spec this out", "SDD", "let's design this before coding", or when requirements are too vague to implement safely. Also use to resume an existing SDD project (a repo with sdd/status.md).
---

# SDD - Specification-Driven Development

Turn an incomplete product idea into a clear, internally consistent,
implementation-ready specification, then implement it task by task with the
spec as the source of truth.

Act as product analyst, requirements engineer, architect, technical reviewer
and implementation planner. Do not rush into coding while important
requirements or architectural decisions are still unclear.

The objective is not to predict every detail before writing code. It is to
eliminate the ambiguity that would otherwise cause expensive rework.

## Start here - every session

1. Look for `sdd/status.md` in the project.
   - **Exists** → read it, then read only the docs it points to for the
     current phase. Resume from there; do not restart discovery.
   - **Missing, empty/new project** → start at Phase 1.
   - **Missing, existing codebase** → start at Phase 0.
2. Tell the user in one or two lines which phase you're in and what's next.

## The status file (`sdd/status.md`)

The single living record that carries the project across sessions. Create it in
the first phase and update it whenever something below changes - not at the
end of the session.

```markdown
# Status

Phase: 3 - Architecture (gate not yet approved)
Next: resolve Q-004, then draft ADR-002

## Confirmed requirements   (explicitly accepted by the user)
## Assumptions              (believed true, NOT confirmed - never treat as requirements)
## Open questions           (Q-001 ... ; mark critical ones [CRITICAL])
## Constraints              (technical, business, legal, operational, budget)
## Decisions                (link ADRs)
## Risks
## Tasks                    (Phase 6-7 only: - [ ] TASK-001 ... with status)
```

Short items can live directly here; once a list grows long, move it to its own
doc and link it.

## Document layout

**Default:** `sdd/status.md` + one `sdd/spec.md` (product, requirements,
architecture and feature specs as sections) + `sdd/decisions/ADR-NNN-*.md`.

Split into the full tree only when `spec.md` passes ~300 lines or the project
has several independent features:

```text
sdd/
├── status.md
├── product/        vision.md, users.md, requirements.md, user-flows.md, scope.md
├── architecture/   overview.md, components.md, data-model.md, api.md, security.md, infrastructure.md
├── decisions/      ADR-001-*.md ...
└── specs/          feature-001-*.md ...
```

Create a document only when enough information exists to make it useful.
Templates for ADRs, feature specs and acceptance criteria are in
[TEMPLATES.md](TEMPLATES.md) - read it when writing one of those.

## Phases and gates

Copy this checklist into your working notes and keep it current:

```text
- [ ] Phase 0: Baseline (existing codebase only)
- [ ] Phase 1: Discovery
- [ ] Phase 2: Requirements & scope
- [ ] Phase 3: Architecture & ADRs
- [ ] Phase 4: Feature specs
- [ ] Phase 5: Readiness check
- [ ] Phase 6: Implementation plan
- [ ] Phase 7: Implementation
```

Each phase ends at a **gate**: summarize what was produced, list remaining open
questions and assumptions, and ask the user to approve before moving on. Only
user-approved items move from Assumptions to Confirmed requirements/Decisions.
The user may reopen any earlier phase at any time - when they do, state the
consequences and update every affected doc.

For small projects, phases can be short and gates can be combined (e.g. 2+3,
or 4+5+6), but never skip the user approval before Phase 7.

### Phase 0 - Baseline (existing codebase)

Before specifying a change to existing code, document what the system does
today: components, data model, external integrations, key flows, and the
conventions the code already follows. Keep it brief and factual - this is the
"current state" the new spec is written against. Mark anything you infer
rather than verify as an assumption.

### Phase 1 - Discovery

Ask the user to describe the product in their own words, then extract and
determine as applicable:

- **Problem** - what it solves, why it matters, what happens without it
- **Users** - user types, permissions, goals
- **Core workflows** - for each: starting condition, user action, system
  behavior, alternatives, failure cases, result
- **Constraints, dependencies, risks**

**Interviewing:** use the `AskUserQuestion` tool, 3-5 high-value questions per
round, then continue based on the answers. Prioritize questions that
materially affect scope, UX, business logic, data model, security, APIs,
architecture, infrastructure, cost or complexity. When it isn't obvious, say
briefly why the answer matters. Never silently invent an important
requirement - record it as an assumption or ask.

### Phase 2 - Requirements & scope

- Write precise, testable requirements with stable IDs (`REQ-001`, ...).
  "Should be fast" is not a requirement; a latency target under a stated
  workload is.
- Explicitly split **in scope / out of scope / future**. Do not let future
  ideas silently become current requirements.
- Include the important non-functional requirements (security, reliability,
  performance, operations).

### Phase 3 - Architecture & ADRs

Only after the major requirements are understood. Describe components and
responsibilities, communication, data ownership, storage, external systems,
authn/authz, key runtime flows, deployment, failure and security boundaries.

Prefer the simplest architecture that satisfies the known requirements. Do not
introduce technology because it is popular - for each major choice, weigh the
requirement served, alternatives, complexity, operational and development
cost, failure modes.

Write an ADR when a decision has meaningful architectural consequences, has
several reasonable alternatives, is hard to reverse, may be questioned later,
or constrains implementation. Not for trivial details. Superseded ADRs are
kept, marked `Superseded`, and link to the new one.

### Phase 4 - Feature specs

One spec per feature (a section of `spec.md` or `specs/feature-NNN-*.md`),
using the template in [TEMPLATES.md](TEMPLATES.md). Every significant feature
gets Given/When/Then acceptance criteria covering failure cases, not just the
happy path. Do not specify undecided implementation details unless necessary.
Keep requirements traceable: features reference `REQ-*`, ADRs reference the
requirements they serve.

### Phase 5 - Readiness check

**Challenge the design** - look for contradictions, missing or ambiguous
behavior, hidden assumptions, unnecessary complexity, premature features,
untestable requirements, and problems with security, scalability, data
consistency, failures, migrations and operations. Phrase findings neutrally
("this creates a consistency problem if X and Y happen simultaneously"), not
"this is a bad design" - the goal is to improve the design, not override the
user.

Then confirm each planned feature is implementation-ready:

- Purpose and behavior are sufficiently defined; edge cases addressed
- Architecture supports it; data changes and API contracts defined
- Security: authn, authz, secrets, sensitive data, input validation, abuse
- Reliability: failures, retries, timeouts, idempotency, recovery, consistency
- Operations: logging, monitoring, backups, deployment, config, migrations
- Acceptance criteria exist; test levels (unit/integration/e2e) identified
- No `[CRITICAL]` open questions remain

A document existing does not make a feature ready. If something critical is
missing, say so explicitly instead of pretending the spec is complete.

### Phase 6 - Implementation plan

Convert specs into tasks (`TASK-001`, ...) in `status.md`. Each task is small
enough to implement and verify independently, ordered by dependency, traceable
to `REQ-*`/feature IDs, and has a clear "done" condition. Avoid hundreds of
tiny tasks - a task is roughly one reviewable commit.

### Phase 7 - Implementation

The accepted specs and ADRs are the source of truth. Work one task at a time:

1. Mark the task in progress in `status.md`.
2. Write or update tests from the task's acceptance criteria first.
3. Implement until those tests pass; run the wider test suite.
4. Tick the task done in `status.md`, then commit (one task per commit,
   message references the TASK/REQ IDs) if the user wants commits.
5. Move to the next task.

**If implementation reveals the spec is wrong or incomplete, stop** - do not
let implementation details silently redefine the product or architecture:

1. Report the problem and the affected requirements/specs.
2. Propose reasonable alternatives and ask the user.
3. Write or supersede an ADR if the change is architectural.
4. Update the affected docs and the task list in `status.md`.
5. Continue.

## Conflicts and source of truth

When documents conflict, do not silently choose one - identify the conflict
and ask. Default precedence:

```text
User-confirmed requirements → accepted ADRs → architecture → feature specs → plan → code
```

If code shows the docs are outdated, do not automatically treat the code as
correct: determine which one reflects the intended current state and update
the others.

## Never

- Invent major requirements or silently expand scope
- Treat assumptions as facts, or hide conflicts between requirements
- Rewrite architecture or make significant irreversible decisions without discussion
- Generate large amounts of code before requirements are sufficiently understood
- Declare a design complete while critical questions remain
