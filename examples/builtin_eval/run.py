#!/usr/bin/env python3
"""
Built-in Evaluator Example
==========================

Uses Azure AI's built-in coherence evaluator to score pre-generated responses.
No inference model needed - just evaluating static data.

Usage:
    python -m builtin_eval.run
    # or from examples directory:
    python builtin_eval/run.py
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
from builtin_eval.data import ITEMS


# Data source configuration for simple query/response pairs
DATA_SOURCE_CONFIG = {
    "type": "custom",
    "item_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "response": {"type": "string"},
        },
        "required": ["query", "response"],
    },
    "include_sample_schema": True,
}


def get_coherence_criterion(model: str):
    """Return testing criterion for built-in coherence evaluator."""
    return {
        "type": "azure_ai_evaluator",
        "name": "coherence",
        "evaluator_name": "builtin.coherence",
        "initialization_parameters": {"deployment_name": model},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    }


def main():
    """Run the built-in evaluator example."""
    print("Built-in Evaluator Example")
    print("=" * 40)

    with get_clients() as (project_client, client):
        eval_obj = client.evals.create(
            name="builtin-coherence-example",
            data_source_config=DATA_SOURCE_CONFIG,
            testing_criteria=[get_coherence_criterion(DEFAULT_JUDGE_MODEL)],
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
