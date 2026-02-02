"""MCP agent creation for cloud evaluation."""

from azure.ai.projects.models import PromptAgentDefinition, MCPTool

from .tools import MCP_SERVER_URL, MCP_SERVER_LABEL


def create_mcp_weather_agent(project_client, model: str, agent_name: str = "MCPWeatherAgent"):
    """Create a weather agent that uses MCP tools.

    Args:
        project_client: The Azure AI project client
        model: The model deployment name to use
        agent_name: Name for the agent

    Returns:
        The created agent object
    """
    mcp_tool = MCPTool(
        server_label=MCP_SERVER_LABEL,
        server_url=MCP_SERVER_URL,
        require_approval="never",  # Required for batch evaluation
    )

    return project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions=(
                "You are a helpful weather assistant. "
                "Use the available tools to get weather information for users."
            ),
            tools=[mcp_tool],
        ),
    )
