#!/usr/bin/env python3
"""
Foundry Agent Evaluation - Main Entry Point
============================================

Runs a two-phase evaluation of a Foundry weather agent:

Phase 1 (azure_ai_responses): Built-in + LLM evaluators
  - task_adherence, intent_resolution, tool_call_accuracy (built-in)
  - response_helpfulness (custom LLM)

Phase 2 (custom/JSONL): Code evaluator
  - response_length (custom code)

Usage:
    python -m foundry_agent_eval.run
    # or from examples directory:
    python foundry_agent_eval/run.py
"""

import sys
import uuid
from pathlib import Path

# Add parent to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import get_clients, wait_for_evaluator, wait_for_completion, print_results, DEFAULT_JUDGE_MODEL
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)

from foundry_agent_eval.evaluators import ResponseLengthEvaluator, ResponseHelpfulnessEvaluator
from foundry_agent_eval.agent import create_weather_agent, run_agent


def get_builtin_criteria(model: str) -> list:
    """Return testing criteria for built-in agent evaluators."""
    return [
        {
            "type": "azure_ai_evaluator",
            "name": "task_adherence",
            "evaluator_name": "builtin.task_adherence",
            "initialization_parameters": {"deployment_name": model},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "intent_resolution",
            "evaluator_name": "builtin.intent_resolution",
            "initialization_parameters": {"deployment_name": model},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "tool_call_accuracy",
            "evaluator_name": "builtin.tool_call_accuracy",
            "initialization_parameters": {"deployment_name": model},
        },
    ]


def run_agent_evaluation(client, response_id: str, criteria: list, run_id: str):
    """Run evaluation using azure_ai_responses data source.

    This evaluation type works with:
    - Built-in agent evaluators
    - Custom LLM (prompt) evaluators

    It does NOT work with custom CODE evaluators.
    """
    eval_config = {"type": "azure_ai_source", "scenario": "responses"}

    eval_obj = client.evals.create(
        name=f"agent-eval-{run_id}",
        data_source_config=eval_config,
        testing_criteria=criteria,
    )
    print(f"  Eval created: {eval_obj.id}")

    data_source = {
        "type": "azure_ai_responses",
        "item_generation_params": {
            "type": "response_retrieval",
            "data_mapping": {"response_id": "{{item.resp_id}}"},
            "source": {
                "type": "file_content",
                "content": [{"item": {"resp_id": response_id}}],
            },
        },
    }

    eval_run = client.evals.runs.create(
        eval_id=eval_obj.id,
        name="agent-evaluators-run",
        data_source=data_source,
    )
    print(f"  Eval run: {eval_run.id}")

    return wait_for_completion(client, eval_obj.id, eval_run.id)


def run_code_evaluation(client, query: str, response_text: str, criteria: list, run_id: str):
    """Run evaluation using custom/JSONL data source.

    This evaluation type works with:
    - Custom CODE evaluators
    - Custom LLM evaluators
    - Built-in evaluators (with appropriate data mapping)

    Use this when you need to evaluate extracted string data.
    """
    eval_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": [],
        },
        "include_sample_schema": True,
    }

    eval_obj = client.evals.create(
        name=f"code-eval-{run_id}",
        data_source_config=eval_config,
        testing_criteria=criteria,
    )
    print(f"  Eval created: {eval_obj.id}")

    eval_data = {"query": query, "response": response_text}
    eval_run = client.evals.runs.create(
        eval_id=eval_obj.id,
        name="code-evaluator-run",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[SourceFileContentContent(item=eval_data)],
            ),
        ),
    )
    print(f"  Eval run: {eval_run.id}")

    return wait_for_completion(client, eval_obj.id, eval_run.id)


def main():
    """Run the two-phase evaluation."""
    run_id = uuid.uuid4().hex[:8]
    print(f"Run ID: {run_id}")

    with get_clients() as (project_client, client):
        # =====================================================================
        # STEP 1: Create Custom Evaluators
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 1: Creating custom evaluators")
        print("=" * 60)

        length_evaluator = ResponseLengthEvaluator(f"response_length_{run_id}")
        length_evaluator.create(project_client)
        print(f"  Created CODE evaluator: {length_evaluator.name} v{length_evaluator.version}")

        helpfulness_evaluator = ResponseHelpfulnessEvaluator(f"response_helpfulness_{run_id}")
        helpfulness_evaluator.create(project_client)
        print(f"  Created LLM evaluator: {helpfulness_evaluator.name} v{helpfulness_evaluator.version}")

        wait_for_evaluator(project_client, length_evaluator.name, length_evaluator.version)
        wait_for_evaluator(project_client, helpfulness_evaluator.name, helpfulness_evaluator.version)

        # =====================================================================
        # STEP 2: Create and Run Agent
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 2: Creating and running agent")
        print("=" * 60)

        agent = create_weather_agent(project_client, DEFAULT_JUDGE_MODEL)
        print(f"  Agent: {agent.name} v{agent.version}")

        user_query = "What is the weather in Seattle?"
        print(f"  Query: {user_query}")

        result = run_agent(client, agent, user_query)
        print(f"  Response ID: {result.response_id}")
        print(f"  Response: {result.response_text[:100]}...")

        # =====================================================================
        # STEP 3: EVALUATION 1 - Agent Evaluators (azure_ai_responses)
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 3: EVALUATION 1 - Built-in + LLM evaluators")
        print("=" * 60)

        criteria_1 = get_builtin_criteria(DEFAULT_JUDGE_MODEL)
        criteria_1.append(helpfulness_evaluator.get_testing_criterion(DEFAULT_JUDGE_MODEL))

        run_1, items_1 = run_agent_evaluation(client, result.response_id, criteria_1, run_id)
        print("\n  === EVAL 1 RESULTS (Agent Evaluators) ===")
        print_results(run_1, items_1)

        # =====================================================================
        # STEP 4: EVALUATION 2 - Code Evaluator (custom data source)
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 4: EVALUATION 2 - Code evaluator")
        print("=" * 60)

        criteria_2 = [length_evaluator.get_testing_criterion()]

        run_2, items_2 = run_code_evaluation(
            client, user_query, result.response_text, criteria_2, run_id
        )
        print("\n  === EVAL 2 RESULTS (Code Evaluator) ===")
        print_results(run_2, items_2)

        # =====================================================================
        # STEP 5: Cleanup
        # =====================================================================
        print("\n" + "=" * 60)
        print("STEP 5: Cleanup")
        print("=" * 60)

        length_evaluator.delete(project_client)
        print(f"  Deleted: {length_evaluator.name}")

        helpfulness_evaluator.delete(project_client)
        print(f"  Deleted: {helpfulness_evaluator.name}")

        print("\n✓ Done!")


if __name__ == "__main__":
    main()
