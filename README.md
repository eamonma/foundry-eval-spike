# Microsoft Foundry Evaluations Investigation

This repo explores Microsoft Foundry (SDK v2) evaluation workflows and edge cases via small scripts.

## Goals
- Understand evaluator types and how they interact (built‑in vs custom, cloud vs local, batch vs non‑batch, agent vs general/custom).
- Clarify evaluation input model (thread/agent response vs simpler query/response items).
- Enable deterministic, tool‑call–level validation via code evaluators.

## Workflow
Run the Python scripts manually (they work when executed directly; running via Claude Code can hit timing/propagation issues).

## Docs
Processed Foundry docs live in `docs/` (key starting points: `general-purpose-evaluators.md`, `agent-evaluators.md`, `custom-evaluators.md`, `cloud-evaluation.md`, `agent-evaluate-sdk.md`).

## Important
Use Microsoft Foundry **SDK v2** only (avoid Foundry Classic / SDK v1).
