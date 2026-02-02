---
title: Agent Evaluation with the Microsoft Foundry SDK
titleSuffix: Microsoft Foundry
description: This article provides instructions on how to evaluate an AI agent with the Microsoft Foundry SDK
monikerRange: 'foundry'
ms.service: azure-ai-foundry
ms.custom: 
- build-2025
- references_regions
ms.topic: how-to
ms.date: 11/25/2025
ms.reviewer: changliu2
ms.author: lagayhar
author: lgayhardt
# customer intent: As a developer, I want to evaluate my AI agents using the Microsoft Foundry SDK so I can assess the quality, safety, and efficiency of agentic workflows.
ai-usage: ai-assisted
---

# Evaluate your AI agents (preview)

[!INCLUDE [version-banner](../../includes/version-banner.md)]

[!INCLUDE [feature-preview](../../includes/feature-preview.md)]

AI agents are powerful productivity assistants that create workflows for business needs. However, observability is challenging because of their complex interaction patterns. In this article, you learn how to evaluate Microsoft Foundry agents or other agents using built-in evaluators.

To build production-ready agentic applications and ensure observability and transparency, developers need tools to assess not only the final output of an agent's workflows but also the quality and efficiency of the workflows.

An event like a user querying "weather tomorrow" triggers an agentic workflow. To produce a final response, the workflow includes reasoning through user intents, calling tools, and using retrieval-augmented generation.

[!INCLUDE [evaluation-preview](../../includes/evaluation-preview.md)]



As a best practice, it's crucial to perform:

- **System Evaluation**: assess the overall quality and efficiency of the agent's workflow; and
- **Process Evaluation**: evaluate tool calling steps of the workflow.

See [agent evaluators](../../concepts/evaluation-evaluators/agent-evaluators.md) for detailed information about the use case of the two practices and a sample of each agent evaluator.

You can also assess other quality and safety aspects of your agentic workflows, using our [comprehensive suite of built-in evaluators](../../concepts/observability.md#what-are-evaluators) or write [custom evaluators](../../concepts/evaluation-evaluators/custom-evaluators.md).

If you're building Foundry Agents, you can [seamlessly evaluate them](#evaluate-microsoft-foundry-agents).

If you build your agents outside of Foundry, you can still use our evaluators as appropriate to your agentic workflow, by parsing your agent messages into the required data formats. See details in [Evaluating other agents](#evaluating-other-agents).


## Get started



Install the package from the Azure AI evaluation SDK:

```python
pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv
```

Set these environment variables with your values in a `.env` file:

```python
AZURE_AI_PROJECT_ENDPOINT="<your-endpoint>" # The Azure AI Project project endpoint, as found in the Home page of your Microsoft Foundry portal.
AZURE_AI_MODEL_DEPLOYMENT_NAME="<your-model-deployment-name>" # The deployment name of the AI model, as found under the "Build" page in the "Models" tab in your Foundry project.
```


## Evaluate Microsoft Foundry agents



You can seamlessly evaluate Foundry agents by using evaluators in [Agent Evaluators](../../concepts/evaluation-evaluators/agent-evaluators.md) and [RAG evaluators](../../concepts/evaluation-evaluators/rag-evaluators.md). This section walks you through creating an agent and evaluating it.

> [!NOTE]
> If you're building other agents that output a different schema, convert them into the general OpenAI-style [agent message schema](#agent-message-schema) and use the preceding evaluators.
> More generally, if you can parse the agent messages into the required data formats, you can also use all of our evaluators.

### Prerequisites

```python
import json
from azure.ai.projects.models import Tool, FunctionTool

# Define a function tool for the model to use
func_tool = fetch_weather(
    name="fetch_weather",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The location to fetch weather for.",
            },
        },
        "required": ["location"],
        "additionalProperties": False,
    },
    description="Get the current weather for a location.",
    strict=True,
)

tools: list[Tool] = [func_tool]

# Define a custom Python function.
async def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.

    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    # In the following code snippet, we mock the response.
    mock_weather_data = {"Seattle": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json

```

Set up an agent with the toolset and create a response run to evaluate.

Create an agent with the toolset as follows:

```python
import os
import json
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import DefaultAzureCredential
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

credential = DefaultAzureCredential()


project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    agent = await project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant that can use function tools.",
            tools=tools,
        ),
    )

    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the weather in Seattle?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text} (id: {response.id})")


    # Now create evaluation for the response
    data_source_config = {"type": "azure_ai_source", "scenario": "responses"}

    # add your desired evaluators here
    testing_criteria = [
        {"type": "azure_ai_evaluator", "name": "task_adherence", "evaluator_name": "builtin.task_adherence"},
        {"type": "azure_ai_evaluator", "name": "groundedness", "evaluator_name": "builtin.groundedness"},
    ]
    eval_object = openai_client.evals.create(
        name="Agent Response Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    data_source = {
        "type": "azure_ai_responses",
        "item_generation_params": {
            "type": "response_retrieval",
            "data_mapping": {"response_id": "{{item.resp_id}}"},
            "source": {"type": "file_content", "content": [{"item": {"resp_id": response.id}}]},
        },
    }

    response_eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id, name=f"Evaluation Run for Agent {agent.name}", data_source=data_source
    )
    print(f"Evaluation run created (id: {response_eval_run.id})")

    while response_eval_run.status not in ["completed", "failed"]:
        response_eval_run = openai_client.evals.runs.retrieve(run_id=response_eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {response_eval_run.status}")
        time.sleep(5)

    if response_eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {response_eval_run.result_counts}")
        print(f"Eval Run Report URL: {response_eval_run.report_url}")
        output_items = list(
            openai_client.evals.runs.output_items.list(run_id=response_eval_run.id, eval_id=eval_object.id)
        )
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")
    else:
        print("\n✗ Evaluation run failed.")

```

### Interpretation of results

For a single data example, all evaluators always output the following schema:  

- **Label**: a binary "pass" or "fail" label, similar to a unit test's output. Use this result to facilitate comparisons across evaluators.
- **Score**: a score from the natural scale of each evaluator. Some evaluators use a fine-grained rubric, scoring on a 5-point scale (quality evaluators) or a 7-point scale (content safety evaluators). Others, like textual similarity evaluators, use F1 scores, which are floats between 0 and 1. The "label" field binarizes any non-binary "score" to "pass" or "fail" based on the "threshold".
- **Threshold**: any non-binary scores are binarized to "pass" or "fail" based on a default threshold, which you can override in the SDK experience.
- **Reason**: To improve intelligibility, all LLM-judge evaluators also output a reasoning field to explain why a certain score is given.
- **Details**: (optional) For some evaluators, such as tool_call_accuracy, there might be a "details" field or flags that contain additional information to help users debug their applications.
For aggregate results over multiple data examples (a dataset), the average rate of the examples with a "pass" forms the passing rate for that dataset.

After the URL, you're redirected to Foundry. You can view your evaluation results in your Foundry project and debug your application. Use "reason" fields and pass/fail to assess the quality and safety performance of your applications. You can run and compare multiple runs to test for regression or improvements.  

Use the Microsoft Foundry SDK Python client library to evaluate your Microsoft Foundry agents, enabling observability and transparency in agent workflows.


## <a name = "evaluating-other-agents"></a> Evaluate other agents



Agents typically emit messages to interact with a user or other agents. Our built-in evaluators can accept simple data types such as strings in `query`, `response`, and `ground_truth` according to the single-turn data input requirements. However, it can be a challenge to extract these simple data types from agent messages, due to the complex interaction patterns of agents and framework differences. For example, a single user query can trigger a long list of agent messages, typically with multiple tool calls invoked. We show examples of agent message schema in [Agent message schema](#agent-message-schema) with `tool_definitions` and `tool_calls` embedded in `query` and `response`. 






### Agent tool calls and definitions



See the following examples of `tool_calls` and `tool_definitions` for `tool_call_accuracy`:

```python
import json 

query = "How is the weather in Seattle?"
tool_calls = [{
                    "type": "tool_call",
                    "tool_call_id": "call_CUdbkBfvVBla2YP3p24uhElJ",
                    "name": "fetch_weather",
                    "arguments": {
                        "location": "Seattle"
                    }
            },
            {
                    "type": "tool_call",
                    "tool_call_id": "call_CUdbkBfvVBla2YP3p24uhElJ",
                    "name": "fetch_weather",
                    "arguments": {
                        "location": "London"
                    }
            }]

tool_definitions = [{
                    "name": "fetch_weather",
                    "description": "Fetches the weather information for the specified location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The location to fetch weather for."
                            }
                        }
                    }
                }]
```


### Agent message schema

In agent message format, `query` and `response` are a list of OpenAI-style messages. Specifically, `query` carries the past agent-user interactions leading up to the last user query and requires the system message (of the agent) at the top of the list. `response` carries the last message of the agent in response to the last user query. 

The expected input format for the evaluators is a Python list of messages as follows:

```
[
  {
    "role": "system" | "user" | "assistant" | "tool",
    "createdAt": "ISO 8601 timestamp",     // Optional for 'system'
    "run_id": "string",                    // Optional, only for assistant/tool in tool call context
    "tool_call_id": "string",              // Optional, only for tool/tool_result
    "name": "string",                      // Present if it's a tool call
    "arguments": { ... },                  // Parameters passed to the tool (if tool call)
    "content": [
      {
        "type": "text" | "tool_call" | "tool_result",
        "text": "string",                  // if type == text
        "tool_call_id": "string",         // if type == tool_call
        "name": "string",                 // tool name if type == tool_call
        "arguments": { ... },             // tool args if type == tool_call
        "tool_result": { ... }            // result if type == tool_result
      }
    ]
  }
]
```

Sample query and response objects:



```python
query = [
    {
        "role": "system",
        "content": "You are an AI assistant interacting with Azure Maps services to serve user requests."
    },
    {
        "createdAt": "2025-04-25T23:55:43Z",
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Find the address for coordinates 41.8781,-87.6298."
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:45Z",
        "run_id": "run_DGE8RWPS8A9SmfCg61waRx9u",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_nqNyhOFRw4FmF50jaCCq2rDa",
                "name": "azure_maps_reverse_address_search",
                "arguments": {
                    "lat": "41.8781",
                    "lon": "-87.6298"
                }
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:47Z",
        "run_id": "run_DGE8RWPS8A9SmfCg61waRx9u",
        "tool_call_id": "call_nqNyhOFRw4FmF50jaCCq2rDa",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "address": "300 South Federal Street, Chicago, IL 60604",
                    "position": {
                        "lat": "41.8781",
                        "lon": "-87.6298"
                    }
                }
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:48Z",
        "run_id": "run_DGE8RWPS8A9SmfCg61waRx9u",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "The address for the coordinates 41.8781, -87.6298 is 300 South Federal Street, Chicago, IL 60604."
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:50Z",
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "What timezone corresponds to 41.8781,-87.6298?"
            }
        ]
    },
]

response = [
    {
        "createdAt": "2025-04-25T23:55:52Z",
        "run_id": "run_DmnhUGqYd1vCBolcjjODVitB",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_qi2ug31JqzDuLy7zF5uiMbGU",
                "name": "azure_maps_timezone",
                "arguments": {
                    "lat": 41.878100000000003,
                    "lon": -87.629800000000003
                }
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:54Z",
        "run_id": "run_DmnhUGqYd1vCBolcjjODVitB",
        "tool_call_id": "call_qi2ug31JqzDuLy7zF5uiMbGU",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "ianaId": "America/Chicago",
                    "utcOffset": None,
                    "abbreviation": None,
                    "isDaylightSavingTime": None
                }
            }
        ]
    },
    {
        "createdAt": "2025-04-25T23:55:55Z",
        "run_id": "run_DmnhUGqYd1vCBolcjjODVitB",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "The timezone for the coordinates 41.8781, -87.6298 is America/Chicago."
            }
        ]
    }
]
```

> [!NOTE]
> The evaluator throws a warning that it can't parse the query (the conversation history up to the current run) or agent response (the response to the query) when their format isn't the expected one.

More examples of agent messages:

```python
import json

# The user asked a question.
query = [
    {
        "role": "system",
        "content": "You are a friendly and helpful customer service agent."
    },
    # Past interactions are omitted. 
    # ...
    {
        "createdAt": "2025-03-14T06:14:20Z",
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Hi, I need help with the last 2 orders on my account #888. Could you please update me on their status?"
            }
        ]
    }
]
# The agent emits multiple messages to fulfill the request.
response = [
    {
        "createdAt": "2025-03-14T06:14:30Z",
        "run_id": "0",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Hello! Let me quickly look up your account details."
            }
        ]
    },
    {
        "createdAt": "2025-03-14T06:14:35Z",
        "run_id": "0",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "tool_call_20250310_001",
                "name": "get_orders",
                "arguments": {
                    "account_number": "888"
                }
            }
        ]
    },
    # Many more messages are omitted. 
    # ...
    # Here is the agent's final response:
    {
        "createdAt": "2025-03-14T06:15:05Z",
        "run_id": "0",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "The order with ID 123 has been shipped and is expected to be delivered on March 15, 2025. However, the order with ID 124 is delayed and should now arrive by March 20, 2025. Is there anything else I can help you with?"
            }
        ]
    }
]

# An example of tool definitions available to the agent:
tool_definitions = [
    {
        "name": "get_orders",
        "description": "Get the list of orders for a given account number.",
        "parameters": {
            "type": "object",
            "properties": {
                "account_number": {
                    "type": "string",
                    "description": "The account number to get the orders for."
                }
            }
        }
    },
    # Other tool definitions are omitted. 
    # ...
]

```


This evaluation schema helps parse agent data outside Agent Service, enabling the use of built-in evaluators to support observability in agent workflows.

## Sample notebooks



Try a sample for each of these evaluators in the [sample repository](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators).


## Related content



- [Azure AI Evaluation SDK client troubleshooting guide](https://aka.ms/azureaieval-tsg)
- [Evaluate Generative AI applications remotely on the cloud](./cloud-evaluation.md)
- [View evaluation results in a Foundry project](../../how-to/evaluate-results.md)

