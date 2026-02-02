"""Weather tool definitions and implementations.

Defines the tools available to the weather agent and provides
mock implementations for testing.
"""

import json
from azure.ai.projects.models import FunctionTool


# Tool definitions for the agent
WEATHER_TOOLS = [
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
    # Internal reasoning tool - required for tool_call_accuracy evaluator
    # Models like gpt-5-mini emit internal "reasoning" tool calls
    FunctionTool(
        name="reasoning",
        description="Internal reasoning tool used by the model for chain-of-thought processing.",
        parameters={"type": "object", "properties": {}},
    ),
]


# Mock weather data for testing
MOCK_WEATHER_DATA = {
    "Seattle": {"weather": "Rainy, 12°C"},
    "London": {"weather": "Cloudy, 15°C"},
    "Tokyo": {"weather": "Sunny, 22°C"},
    "New York": {"weather": "Clear, 18°C"},
    "Paris": {"weather": "Partly cloudy, 14°C"},
}


def fetch_weather(location: str) -> dict:
    """Mock weather function that returns fake weather data."""
    return MOCK_WEATHER_DATA.get(
        location,
        {"weather": f"Weather data not available for {location}"}
    )


def execute_tool_call(tool_name: str, arguments: str) -> dict:
    """Execute a tool call by name and return the result.

    Args:
        tool_name: The name of the tool to execute
        arguments: JSON string of arguments

    Returns:
        The tool result as a dictionary
    """
    args = json.loads(arguments)

    if tool_name == "fetch_weather":
        return fetch_weather(**args)
    elif tool_name == "reasoning":
        # Reasoning tool doesn't need execution
        return {}
    else:
        return {"error": f"Unknown tool: {tool_name}"}
