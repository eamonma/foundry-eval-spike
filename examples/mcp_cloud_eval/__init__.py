"""MCP Cloud Evaluation Example.

Demonstrates fully cloud-based evaluation of agents using MCP tools:

1. Agent is created with MCP tools (require_approval="never" for batch eval)
2. Evaluation runs entirely in the cloud via azure_ai_target_completions
3. Tool call accuracy evaluator works with MCP tool calls

Key Discoveries (empirically discovered - NOT in official Microsoft docs):

1. MCP tool calls CAN be evaluated by built-in evaluators

2. You must include definitions for internal tools (mcp_list_tools, reasoning)
   Otherwise: "Tool definitions for all tool calls must be provided"

3. Data mapping semantics for azure_ai_target_completions:
   - {{item.*}} = INPUT data you provide (query, tool_definitions, etc.)
     (This IS documented in official docs)
   - {{sample.*}} = OUTPUT data from running the agent (UNDOCUMENTED):
     - {{sample.output_text}} = final text response only
     - {{sample.output_items}} = full response with tool calls
     - {{sample.tool_calls}} = extracted tool call history
     - {{sample.tool_definitions}} = (empty for MCP agents)

4. Map response to {{sample.output_items}}, NOT {{sample.output_text}}
   The evaluators need to see the tool call history to properly assess.

NOTE: We searched the official Azure AI Foundry docs and found NO documentation
for {{sample.*}} variables. The official docs only show {{item.*}} examples.
These sample.* mappings were discovered through trial and error.

This enables fully serverless agent evaluation - no local tool execution needed.
"""
