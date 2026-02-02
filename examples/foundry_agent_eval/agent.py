"""Agent creation and execution logic.

Handles creating Foundry agents and running the tool call loop
to get responses.
"""

import json
from dataclasses import dataclass
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput

from .tools import WEATHER_TOOLS, execute_tool_call


@dataclass
class AgentResponse:
    """Result of running an agent with a query."""
    response_id: str
    response_text: str
    raw_response: object


def create_weather_agent(project_client, model: str, agent_name: str = "WeatherAgent"):
    """Create a weather assistant agent.

    Args:
        project_client: The Azure AI project client
        model: The model deployment name to use
        agent_name: Name for the agent

    Returns:
        The created agent object
    """
    return project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions=(
                "You are a helpful weather assistant. "
                "Use the fetch_weather tool to get weather information. "
                "Provide helpful context like practical advice or temperature conversions."
            ),
            tools=WEATHER_TOOLS,
        ),
    )


def run_agent(client, agent, query: str, max_iterations: int = 5) -> AgentResponse:
    """Run the agent with a query and execute tool calls.

    Args:
        client: The OpenAI client
        agent: The agent to run
        query: The user query
        max_iterations: Maximum tool call iterations

    Returns:
        AgentResponse with the final response
    """
    # Initial request
    response = client.responses.create(
        input=query,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    # Tool call execution loop
    for _ in range(max_iterations):
        function_calls = [
            item for item in response.output
            if item.type == "function_call" and item.name != "reasoning"
        ]

        if not function_calls:
            break

        # Execute each tool call
        input_list = []
        for item in function_calls:
            result = execute_tool_call(item.name, item.arguments)
            input_list.append(
                FunctionCallOutput(
                    type="function_call_output",
                    call_id=item.call_id,
                    output=json.dumps(result),
                )
            )

        # Continue the conversation with tool results
        response = client.responses.create(
            input=input_list,
            previous_response_id=response.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

    # Extract final response text
    response_text = extract_response_text(response)

    return AgentResponse(
        response_id=response.id,
        response_text=response_text,
        raw_response=response,
    )


def extract_response_text(response) -> str:
    """Extract the text content from an agent response."""
    text_parts = []
    for item in response.output:
        if item.type == "message":
            for content_item in item.content:
                if hasattr(content_item, "text"):
                    text_parts.append(content_item.text)
    return "".join(text_parts)
