#!/usr/bin/env python3
"""
Custom LLM Evaluator Example
============================

Creates a custom prompt-based evaluator that uses an LLM to judge
response helpfulness on a 1-5 scale.

Usage:
    python -m custom_llm_eval.run
    # or from examples directory:
    python custom_llm_eval/run.py
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
from custom_llm_eval.evaluator import HelpfulnessJudgeEvaluator
from custom_llm_eval.data import ITEMS


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
    """Run the custom LLM evaluator example."""
    print("Custom LLM Evaluator Example")
    print("=" * 40)

    evaluator = HelpfulnessJudgeEvaluator("example_helpfulness_judge")

    with get_clients() as (project_client, client):
        # Create the evaluator
        evaluator.create(project_client)
        print(f"Created evaluator: {evaluator.name} v{evaluator.version}")

        try:
            # Create and run evaluation
            eval_obj = client.evals.create(
                name="custom-llm-eval-example",
                data_source_config=DATA_SOURCE_CONFIG,
                testing_criteria=[
                    evaluator.get_testing_criterion(DEFAULT_JUDGE_MODEL)
                ],
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
