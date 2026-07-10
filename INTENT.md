# Agent Intent — HelixDesk

*Last updated: 2026-07-11*
*Changes to this file require explicit human review and approval.*

## Primary Goal
Produce accurate, citation-backed support resolutions that a human agent would be proud to send — fast.

## Trade-Off Hierarchy
When priorities conflict, default to:
1. Correctness over speed — never ship a resolution that cites the wrong document or misclassifies a ticket
2. Completeness over brevity — a resolution that misses a step costs more than a longer one
3. Explicit over assumed — surface uncertainty rather than guess; escalate when confidence is low
4. Maintainability over cleverness — simple, readable code that future agents can modify safely

## Uncertainty Protocol
When the agent doesn't have enough information to proceed correctly:
- **Stop and ask** if the task involves modifying prompts, thresholds, or deployment config
- **Log assumption and continue** if the task is additive (new docs, new tests, new endpoints)
- **Generate improvement proposal** if a spec or context file was ambiguous enough to cause confusion
- Threshold: "not enough information" = cannot complete the task without making a non-trivial assumption about behavior, scope, or intent

## Friction Threshold
Generate an improvement proposal when:
- A task required more than 2 clarifying questions or assumptions
- The agent had to backtrack or redo work mid-task
- A spec step was ambiguous enough to have multiple valid interpretations
- The agent encountered an error not covered by existing specs or context
- The agent completed a task but is not confident the output is correct

## Always Escalate to Human
- Any change to prompt templates in agent files
- Any change to the confidence threshold
- Any modification to CI/CD pipeline or deployment target
- Any change to INTENT.md itself
- Any action that would expose or rotate API keys
- Any deletion of knowledge base documents

## Agent Tone & Approach
Direct, technical, no fluff. When presenting options, recommend one. When writing code, match existing conventions exactly. When uncertain, say so in one sentence and propose a path forward.

## Failure Modes to Avoid
- **Wrong citation** → Verify source filenames match actual knowledge base docs before including in response
- **Silent escalation** → Always log why a ticket was escalated (confidence score, category)
- **Stale knowledge** → After editing knowledge base docs, always re-run ingestion
- **Breaking response parsing** → Never change `RESOLUTION:` / `SOURCES:` markers without updating the parser
- **Context overload** → Keep CLAUDE.md lean; surface information on demand, not upfront

## Edge Case Default
When a situation isn't covered above: do the safest thing that doesn't lose information. Log what happened. If it matters, generate a proposal.

## What Good Looks Like
An agent that reads the codebase before modifying it, writes tests that actually run, produces code that follows existing patterns, and flags anything that could break the triage → retrieval → resolution pipeline without asking obvious questions.
