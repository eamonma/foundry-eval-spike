"""Test data for MCP cloud evaluation."""

from .tools import ALL_TOOL_DEFINITIONS

# Test queries to run against the MCP agent
TEST_ITEMS = [
    {
        "query": "What's the weather in Seattle?",
        "tool_definitions": ALL_TOOL_DEFINITIONS,
    },
    {
        "query": "What's the weather where I am?",
        "tool_definitions": ALL_TOOL_DEFINITIONS,
    },
    {
        "query": "Is it raining in Tokyo?",
        "tool_definitions": ALL_TOOL_DEFINITIONS,
    },
]
