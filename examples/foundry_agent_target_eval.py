"""
Test: Evaluate a Foundry agent by targeting it with test inputs.

Approach 2: Point evaluation at an existing agent, provide test queries,
and the evaluation system runs the agent and evaluates the outputs.
This evaluates *new* responses generated during the evaluation run.
"""

import time
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from eval_utils import get_clients, print_results, DEFAULT_JUDGE_MODEL

# --- Define tools for the agent ---
tools = [
    FunctionTool(
        name="fetch_weather",
        description="Get the current weather for a location.",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to fetch weather for.",
                },
            },
            "required": ["location"],
        },
    ),
]

# --- Test queries to run against the agent ---
test_items = [
    {"query": "What is the weather in Seattle?"},
    {"query": "Tell me the weather in Tokyo."},
    {"query": "How's the weather in London today?"},
]

# --- Run ---
with get_clients() as (project_client, client):
    # 1. Create a Foundry agent (or use an existing one)
    print("Creating Foundry agent...")
    agent = project_client.agents.create_version(
        agent_name="WeatherAgentTarget",
        definition=PromptAgentDefinition(
            model=DEFAULT_JUDGE_MODEL,
            instructions="You are a helpful weather assistant. Use the fetch_weather tool to get weather information.",
            tools=tools,
        ),
    )
    print(f"Agent created: {agent.name} v{agent.version}")

    # 2. Create evaluation
    print("\nCreating evaluation...")
    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        "include_sample_schema": True,
    }

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "task_completion",
            "evaluator_name": "builtin.task_completion",
            "initialization_parameters": {"deployment_name": DEFAULT_JUDGE_MODEL},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "tool_call_accuracy",
            "evaluator_name": "builtin.tool_call_accuracy",
            "initialization_parameters": {"deployment_name": DEFAULT_JUDGE_MODEL},
        },
    ]

    eval_obj = client.evals.create(
        name="foundry-agent-target-eval",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Eval created: {eval_obj.id}")

    # 3. Run evaluation targeting the agent
    # The evaluation system will run the agent with each test query
    data_source = {
        "type": "azure_ai_target_completions",
        "source": {
            "type": "file_content",
            "content": [{"item": item} for item in test_items],
        },
        "input_messages": {
            "type": "template",
            "template": [
                {
                    "type": "message",
                    "role": "developer",
                    "content": {
                        "type": "input_text",
                        "text": "You are a helpful weather assistant.",
                    },
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": {
                        "type": "input_text",
                        "text": "{{item.query}}",
                    },
                },
            ],
        },
        "target": {
            "type": "azure_ai_agent",
            "name": agent.name,
            "version": agent.version,
        },
    }

    eval_run = client.evals.runs.create(
        eval_id=eval_obj.id,
        name=f"target-eval-{agent.name}",
        data_source=data_source,
    )
    print(f"Eval run created: {eval_run.id}")

    # 4. Wait for completion
    print("\nWaiting for evaluation (agent will be invoked for each test query)...")
    while eval_run.status not in ("completed", "failed"):
        eval_run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_obj.id)
        print(f"  Status: {eval_run.status}")
        time.sleep(3)

    output_items = list(client.evals.runs.output_items.list(run_id=eval_run.id, eval_id=eval_obj.id))
    print_results(eval_run, output_items)
