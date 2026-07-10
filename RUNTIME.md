# Runtime — HelixDesk

*Self-improving agent operating system. Activates after onboarding completes.*

## Session Start Protocol
Every session in this repo:
1. Read `CLAUDE.md` — loads context
2. Read `INTENT.md` — loads goals and trade-off hierarchy
3. Check `IMPROVEMENT_QUEUE.md` — note any open proposals (don't interrupt task for them)
4. Check `LOGS/errors/` — note any recent errors relevant to current task
5. Confirm the relevant spec exists before starting task work

## Friction Detection
During task execution, track friction in real time:
- Making an assumption because the spec or context didn't cover a case
- Asking a clarifying question that a better spec would have answered
- Backtracking or redoing work because initial understanding was wrong
- Encountering an error not covered by existing error handling
- Completing a task but lacking confidence the output meets the quality bar
- Encountering ambiguity with multiple valid interpretations

Each friction event gets logged internally. At task completion, evaluate against the threshold in `INTENT.md`. If threshold is met or exceeded: generate a proposal.

## Error Logging
When an unexpected error occurs:
1. Log immediately to `LOGS/errors/[date]-[task]-[N].md`
2. Evaluate whether to stop and escalate or log and continue based on `INTENT.md` uncertainty protocol
3. If the error indicates a structural gap: generate an improvement proposal

## *reflect Command
When triggered manually or at natural task completion checkpoints:
1. Review friction events from current session
2. Review any new error logs
3. Evaluate against friction threshold in `INTENT.md`
4. Generate proposals for anything that meets the threshold
5. Report to user: "Reflected on [N] tasks. Generated [N] proposals. Use *review to see them."

## *review Command
When triggered:
1. Open `IMPROVEMENT_QUEUE.md`
2. Surface all proposals with status `PENDING`
3. For each proposal, present with a recommended action
4. Accept user decision: approve / reject / modify
5. On approval: apply the change, update status, increment spec version
6. On rejection: update status with reason
7. On modify: user edits inline, agent applies modified version

**INTENT.md proposals require explicit `APPROVE INTENT CHANGE` confirmation.**

## *status Command
Report current environment health: spec coverage, open proposals, recent activity, health flags.
