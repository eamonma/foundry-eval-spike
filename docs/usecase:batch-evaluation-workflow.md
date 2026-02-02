# Batch Evaluation Workflow with Ground Truth

## Desired Use Case

Run agents on a predefined list of prompts (JSONL), where each row includes ground truth. Decouple execution from evaluation so they can run at different times.

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Agent Execution                                    │
│                                                             │
│   input.jsonl ─────────► Run Agent ─────────► output.jsonl  │
│   [prompt, ground_truth]     │              [prompt,        │
│                              │               ground_truth,  │
│                              │               response_id,   │
│                              │               response_data] │
└─────────────────────────────────────────────────────────────┘
                              ⋮
                         (time passes)
                              ⋮
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Evaluation                                         │
│                                                             │
│   output.jsonl ─────────► Evaluators ─────────► Results     │
│   [response + ground_truth]  (built-in or custom)           │
└─────────────────────────────────────────────────────────────┘
```

## Key Questions

### 1. Can we include ground_truth alongside response IDs?

**Likely yes.** The data source item is just a dict:

```python
"source": {"type": "file_content", "content": [
    {"item": {"resp_id": "resp_123", "ground_truth": "Paris"}},
    {"item": {"resp_id": "resp_456", "ground_truth": "Tokyo"}},
]}
```

The `response_retrieval` mechanism uses `resp_id` to fetch agent data, but other fields like `ground_truth` should pass through for evaluators to use in `data_mapping`.

### 2. Which evaluators can use ground_truth?

| Evaluator Type | Ground Truth Support |
|----------------|---------------------|
| `task_navigation_efficiency` | **Required** - expects ground truth tool sequence |
| RAG evaluators (`groundedness`, `relevance`) | Can use context/ground_truth |
| Custom code evaluator | **Full control** - you define what `grade(sample, item)` does with it |
| Custom LLM evaluator | **Full control** - template can include `{{ground_truth}}` |
| Other agent evaluators | Mostly don't use it (they assess the thread itself) |

### 3. Response persistence - the "later" problem

**Approach A: Save response IDs only**
- Pro: Simple, Foundry stores the full response data
- Con: Depends on Foundry retention policy - responses might expire
- Con: Requires network access to Foundry at evaluation time

**Approach B: Save full response data**
- Pro: Fully decoupled, can evaluate offline, no retention concerns
- Con: Must preserve the exact agent message format the evaluators expect
- Con: Larger files

**Recommendation**: Save BOTH response_id AND the full response thread. Use IDs if still valid, fall back to saved data if not.

### 4. Data source options for evaluation

| Data Source Type | Use Case |
|-----------------|----------|
| `azure_ai_responses` + `response_retrieval` | Fetch by response ID from Foundry |
| `custom` + `jsonl` | Provide full data yourself (agent message threads) |
| `file_id` | Load from uploaded dataset |

### 5. What to preserve in output JSONL

**Minimum (requires Foundry access later):**
```jsonl
{"prompt": "...", "ground_truth": "...", "response_id": "resp_xxx"}
```

**Resilient (supports offline evaluation):**
```jsonl
{
  "prompt": "...",
  "ground_truth": "...",
  "response_id": "resp_xxx",
  "query": [...],
  "response": [...],
  "tool_definitions": [...]
}
```

## Summary

| Requirement | Feasibility |
|-------------|-------------|
| Batch agent execution → save to file | ✅ Doable |
| Include ground_truth in evaluation | ✅ Yes, for custom evaluators and some built-ins |
| Decouple execution and evaluation | ✅ Yes, via response IDs or saved response data |
| Use JSONL for input and output | ✅ Yes |

**Main uncertainty**: Whether `azure_ai_responses` data source correctly passes through extra fields like `ground_truth` to evaluators. Needs testing.

**Safest path**: Use custom evaluators (code or LLM) which give full control over how ground_truth is used.

## TODO

- [ ] Test if extra fields in `azure_ai_responses` items pass through to evaluators
- [ ] Implement batch execution script that saves response data
- [ ] Implement evaluation script that loads saved data + ground_truth
- [ ] Test with custom code evaluator using ground_truth
