---
name: spec
description: Define requirements before implementation. Clarify success, failure, escalation, completion criteria, preconditions, and allowed autonomy before planning or coding.
---

# Spec

## Purpose

Define requirements before implementation.
Clarify what success means, what must count as failure, what assumptions must be confirmed, where autonomy ends, and when the AI must stop and ask for human judgment.

## Use This Skill To

- Turn an ambiguous request into an implementation-ready spec
- Define required outcomes instead of implementation steps
- Clarify completion criteria before planning or coding
- Clarify success, failure, and escalation boundaries
- Confirm preconditions that the AI must not fill in by guesswork
- Separate required behaviors, constraints, out-of-scope items, and allowed autonomy

## Core Principle

Spec is not a procedure.
Its job is to give the AI a clear basis for judging:

- what must be achieved
- what must not happen
- what is still uncertain
- when to stop autonomous work
- when human confirmation is required

Prioritize:

- Background
- Purpose
- Required behaviors
- Success conditions
- Failure conditions
- Escalation conditions
- Allowed autonomy
- Non-functional requirements
- Constraints
- Out of scope
- Acceptance checks
- Completion criteria
- Definition of done
- Preconditions

Choose plan and implementation details only after the spec is clear and the codebase has been inspected.

## Process

1. Check `tasks/todo.md` for unfinished `spec:` items first.
2. Clarify the background and purpose of the request.
3. Clarify the completion criteria: what would make this work clearly correct.
4. Clarify externally observable required behaviors.
5. Clarify success conditions, failure conditions, and escalation conditions.
6. Clarify non-functional requirements, constraints, and out-of-scope items when needed.
7. Clarify preconditions that must not be inferred by "reading the room."
8. Clarify which implementation details the AI may decide autonomously.
9. If the work is high-risk, treat process constraints themselves as part of the spec.
10. Summarize the result as a short structured spec.
11. Wait for approval before implementation.

## Interview Rules

- Ask about outcomes before implementation methods.
- Use questions to clarify what must be true when the work is done.
- Do not fix file structure, libraries, or implementation steps early unless they are real constraints.
- Do not silently fill omitted assumptions by guesswork.
- Explicitly confirm preconditions where a human might say, "you should already know that."
- Do not silently choose between multiple plausible interpretations.
- Keep questions minimal, but prioritize anything required to judge completion correctly.
- Clarify failure and stop conditions, not only success conditions.
- Make the boundary of allowed autonomy explicit.

## What To Clarify

### Background

- What is the current situation?
- What problem exists now?

### Purpose

- Who needs to be able to do what?
- Why is this change needed?

### Completion Criteria

- What would make the result clearly correct?
- What can be checked to decide the work is done?

### Required Behaviors

- What observable behaviors are required?
- Which requirements are highest priority?

### Success Conditions

- What counts as success?
- Which conditions can the AI evaluate by itself to decide the work is complete?
- Are there measurable limits such as time, count, percentage, confidence threshold, or latency?

### Failure Conditions

- What must not happen?
- What states must never be treated as complete?
- Which failures require an immediate stop, and which failures may be fixed and retried?

### Escalation Conditions

- Under what conditions is human confirmation required?
- Who should be asked?
- How much uncertainty is acceptable before escalation is required?
- Is there a confidence threshold?

### Allowed Autonomy

- Which implementation details may the AI decide by following existing conventions?
- Which choices are safe only after preconditions are explicit?

### Non-Functional Requirements

- Performance
- Safety
- Maintainability
- Compatibility
- Accessibility
- Observability

### Constraints

- What must not change?
- What technologies or policies are mandatory?
- What dependencies must not be added?
- What security boundaries matter?

### Out Of Scope

- What is not included in this task?
- What should be deferred to a separate task?

### Preconditions

- What shared assumptions must be made explicit for the request to be interpreted correctly?
- Are there terms, audiences, operating conditions, or existing rules that could be interpreted differently?
- Which questions block safe autonomous judgment until they are clarified?

### Definition Of Done

- What common completion checks must be satisfied before the work is treated as done?
- Which tests, validation steps, or reports are required?

## Distinctions

### Success Conditions vs Acceptance Checks

- Success conditions are the higher-level criteria the AI uses to judge whether the work is complete.
- Acceptance checks are concrete verifiable checks for individual requirements.

### Completion Criteria vs Definition Of Done

- Completion criteria describe when the requested outcome is correct.
- Definition of done describes when the implementation work may be treated as complete overall.

## When Process Constraints Belong In Spec

Include process requirements in the spec when sequence and controls are themselves part of correctness, for example:

- Payments
- Authentication
- Permission changes
- Production data deletion
- Personal data handling
- Security-sensitive changes
- Data migrations
- Backup and restore
- Auditable workflows

## Output

Summarize the understanding in a short block such as:

```text
Background:
Purpose:
Required behaviors:
Success conditions:
Failure conditions:
Escalation conditions:
Allowed autonomy:
Completion criteria:
Non-functional requirements:
Constraints:
Out of scope:
Preconditions:
Acceptance checks:
Definition of done:
```

## Judgment Stop Conditions

Do not treat the work as complete. Do not guess. Ask for clarification if any of the following is true:

- The success conditions cannot be evaluated.
- A required precondition is still unresolved.
- It is unclear whether a failure condition has been triggered.
- An escalation condition may apply and cannot be ruled out.
- Definition of done cannot be verified.

## Guardrails

- Do not start implementation before completion criteria are clear enough to verify.
- Do not treat implementation steps as the spec unless they are true constraints.
- Do not rely on implicit assumptions the user did not confirm.
- Do not silently choose between ambiguous interpretations.
- Do not widen scope without calling it out.
- In high-risk work, do not omit required process constraints.
- Do not use autonomous judgment on points blocked by unresolved preconditions.
- Keep success conditions, failure conditions, escalation conditions, and definition of done distinct.
