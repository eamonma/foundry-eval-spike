"""Foundry Agent Evaluation Example.

Demonstrates evaluating Foundry agents using a two-phase approach:

1. AGENT EVALUATION (azure_ai_responses data source):
   - Built-in evaluators: task_adherence, intent_resolution, tool_call_accuracy
   - Custom LLM evaluator: response_helpfulness
   - These work with azure_ai_responses because they can handle agent message format

2. SIMPLE EVALUATION (custom data source with JSONL):
   - Custom CODE evaluator: response_length
   - Code evaluators require simple string data, not agent message arrays
   - We extract the response text and evaluate it separately

Key Findings:
- Custom CODE evaluators don't work with azure_ai_responses data source
- Custom LLM (prompt) evaluators DO work with azure_ai_responses
- Built-in agent evaluators work with azure_ai_responses
- Solution: Run two evaluations with different data sources
"""
