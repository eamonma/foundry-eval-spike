#!/usr/bin/env python3
"""
Agent Built-in Evaluator Example
=================================

Uses built-in agent evaluators (tool_call_accuracy) with message thread data.
Key difference from simple evaluators: input is message thread arrays,
not plain strings.

Usage:
    python -m agent_builtin_eval.run
    # or from examples directory:
    python agent_builtin_eval/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from shared import get_clients, wait_for_completion, print_results, DEFAULT_JUDGE_MODEL
from agent_builtin_eval.data import ITEMS


# Data source configuration for agent message threads
# Note: schema uses arrays/objects for agent message format
DATA_SOURCE_CONFIG = {
    "type": "custom",
    "item_schema": {
        "type": "object",
        "properties": {
            "query": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "object"}},
                ]
            },
            "response": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "array", "items": {"type": "object"}},
                ]
            },
            "tool_definitions": {
                "anyOf": [
                    {"type": "object"},
                    {"type": "array", "items": {"type": "object"}},
                ]
            },
        },
        "required": ["query", "response", "tool_definitions"],
    },
    "include_sample_schema": True,
}


def get_tool_call_accuracy_criterion(model: str):
    """Return testing criterion for built-in tool_call_accuracy evaluator."""
    return {
        "type": "azure_ai_evaluator",
        "name": "tool_call_accuracy",
        "evaluator_name": "builtin.tool_call_accuracy",
        "initialization_parameters": {"deployment_name": model},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
            "tool_definitions": "{{item.tool_definitions}}",
        },
    }


def main():
    """Run the agent built-in evaluator example."""
    print("Agent Built-in Evaluator Example")
    print("=" * 40)

    with get_clients() as (project_client, client):
        eval_obj = client.evals.create(
            name="agent-builtin-tool-accuracy-example",
            data_source_config=DATA_SOURCE_CONFIG,
            testing_criteria=[get_tool_call_accuracy_criterion(DEFAULT_JUDGE_MODEL)],
        )
        print(f"Eval created: {eval_obj.id}")

        eval_run = client.evals.runs.create(
            eval_id=eval_obj.id,
            name="run",
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(
                    type="file_content",
                    content=[SourceFileContentContent(item=item) for item in ITEMS],
                ),
            ),
        )
        print(f"Eval run: {eval_run.id}")

        run, output_items = wait_for_completion(client, eval_obj.id, eval_run.id)
        print_results(run, output_items)


if __name__ == "__main__":
    main()
