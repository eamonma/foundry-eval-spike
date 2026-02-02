#!/usr/bin/env python3
"""
Custom Code Evaluator Example
=============================

Creates a custom code-based evaluator that uses pure Python logic
to score responses by length. No LLM judge involved.

Usage:
    python -m custom_code_eval.run
    # or from examples directory:
    python custom_code_eval/run.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from shared import get_clients, wait_for_completion, print_results
from custom_code_eval.evaluator import LengthCheckerEvaluator
from custom_code_eval.data import ITEMS


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


def main():
    """Run the custom code evaluator example."""
    print("Custom Code Evaluator Example")
    print("=" * 40)

    evaluator = LengthCheckerEvaluator("example_length_checker")

    with get_clients() as (project_client, client):
        # Create the evaluator
        evaluator.create(project_client)
        print(f"Created evaluator: {evaluator.name} v{evaluator.version}")

        try:
            # Create and run evaluation
            eval_obj = client.evals.create(
                name="custom-code-eval-example",
                data_source_config=DATA_SOURCE_CONFIG,
                testing_criteria=[evaluator.get_testing_criterion()],
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

        finally:
            # Cleanup
            evaluator.delete(project_client)
            print(f"Deleted evaluator: {evaluator.name}")


if __name__ == "__main__":
    main()
