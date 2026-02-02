# Microsoft Foundry Evaluations Investigation

## Project Purpose

This project investigates Microsoft Foundry evaluations through scripts that test particular slices of functionality.

## Workflow

**User runs Python scripts manually.** The scripts work when the user runs them directly but encounter propagation/timing issues when run from Claude Code.

## Documentation

Downloaded Microsoft Foundry documentation articles are in `docs/` (processed, Foundry Classic content stripped) with originals in `docs/raw/`.

**Most relevant articles** (subjective):
- `general-purpose-evaluators.md` - General purpose evaluators
- `agent-evaluators.md` - Agent evaluators
- `custom-evaluators.md` - Custom evaluators (code-based and prompt-based)
- `cloud-evaluation.md` - Run evaluations in the cloud
- `agent-evaluate-sdk.md` - Evaluate your AI agents

## Critical: SDK Version Confusion

**Important:** There are two Microsoft Foundry versions that are easy to confound:

- **DO NOT USE:** Microsoft Foundry Classic / Microsoft Foundry SDK v1
- **USE THIS:** Microsoft Foundry new / Microsoft Foundry SDK v2

Much of the documentation in training data or web searches references the older Classic/v1 versions. **Do not assume anything about the Foundry SDK without grounding in current v2 documentation.**

## Open Questions

### Evaluation Dimensions

It's unclear how evaluations differ across these dimensions and how they interact:

1. **Built-in vs Custom** evaluators
2. **Cloud vs Non-cloud** evaluations
3. **Batch vs Non-batch** evaluations
4. **Agent evaluators vs General purpose evaluators vs Custom evaluators**

Are there additional dimensions to consider?

### Thread-Based Evaluation Model

- Is evaluation in Foundry new/SDK v2 based on threads?
- Is the starting point of an evaluation always a full query → tool call → tool call → ... → response thread from an agent run?
- Or is it something else?

### Granular Tool Call Evaluation

Can I evaluate a **particular tool call within a thread** independently?

#### Example Scenario

User query: "Find me the last three months sales data"

Available tools:
1. `list_tables` - Lists all tables in the database
2. `search_tables` - Semantically searches tables, returns most relevant ones
3. `query_database` - Runs SQL queries

**Desired evaluation:** Verify that the `query_database` tool call only queries tables that were returned by a previous tool call (either `list_tables` or `search_tables`).

**Key requirements:**
- Do NOT want an LLM evaluator that passes the entire thread and outputs a judgment
- Want to evaluate the `query_database` tool call in isolation
- Input to evaluation: only the table names returned from the search/list tool
- Evaluation question: "Did the agent query ONLY tables from the returned list, nothing else?"

This is a targeted, deterministic evaluation of tool call validity given prior context—not a holistic thread assessment.

#### Code Evaluator Approach

Foundry documentation indicates support for **code evaluators**. This enables a fully deterministic evaluation pipeline:

1. **Extract known tables** (deterministic): Get the list of table names returned from `list_tables`, `search_tables`, or `get_table_names` tool calls
2. **Parse the query** (deterministic): Check the SQL query for syntactic validity
3. **Extract queried tables** (deterministic): If valid SQL, parse out the tables referenced in the query—no LLM needed
4. **Subset comparison** (deterministic): Check if `queried_tables ⊆ known_tables`

This entire flow uses code-based evaluation with no language model involvement—pure parsing and set operations.
