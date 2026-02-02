"""MCP tool definitions for cloud evaluation.

When evaluating MCP agents, you must provide tool definitions that match
what the MCP server exposes. Additionally, you must include definitions
for internal tools that the agent uses:

- mcp_list_tools: Called automatically to discover available tools
- reasoning: Internal chain-of-thought processing

Without these, the tool_call_accuracy evaluator will fail with
"Tool definitions for all tool calls must be provided."
"""

# MCP Server configuration
MCP_SERVER_URL = "https://mcp.eamon.io/mcp?tools=get_weather,get_location"
MCP_SERVER_LABEL = "weather-mcp"

# Tool definitions matching the MCP server's tools
# These should match what mcp_list_tools returns
WEATHER_TOOLS = [
    {
        "name": "get_weather",
        "description": "Returns the current weather for a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The location to get weather for",
                }
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_location",
        "description": "Returns the user's current location.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

# Internal tool definitions required for MCP evaluation
# These are called by the system, not by user intent
INTERNAL_TOOLS = [
    {
        "name": "mcp_list_tools",
        "description": "Internal operation. Disregard these calls; they are called by the harness.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "reasoning",
        "description": "Internal operation. Disregard these calls; they are called by the harness.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
]

# Combined definitions for evaluation
ALL_TOOL_DEFINITIONS = WEATHER_TOOLS + INTERNAL_TOOLS
