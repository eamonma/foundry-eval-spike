"""Sample agent message threads for agent evaluator examples.

Scenario: A database assistant agent that helps users query sales data.
Tools: list_tables, search_tables, query_database

We have two sample threads:
1. GOOD: Agent searches tables, finds relevant ones, queries only those
2. BAD: Agent queries a table that was never returned by search
"""

# Tool definitions available to the agent
TOOL_DEFINITIONS = [
    {
        "name": "list_tables",
        "description": "Lists all tables in the database.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "search_tables",
        "description": "Semantically searches tables and returns the most relevant ones for a query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant tables.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "query_database",
        "description": "Executes a SQL query against the database.",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "The SQL query to execute.",
                }
            },
            "required": ["sql"],
        },
    },
]

# -----------------------------------------------------------------------------
# SAMPLE 1: GOOD - Agent queries only tables returned by search
# -----------------------------------------------------------------------------

GOOD_QUERY = [
    {
        "role": "system",
        "content": "You are a database assistant. You help users query sales data. "
        "Always search for relevant tables before running queries. "
        "Only query tables that exist in the database.",
    },
    {
        "createdAt": "2025-01-15T10:00:00Z",
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Find me the last three months of sales data.",
            }
        ],
    },
]

GOOD_RESPONSE = [
    {
        "createdAt": "2025-01-15T10:00:02Z",
        "run_id": "run_good_001",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_001",
                "name": "search_tables",
                "arguments": {"query": "sales data monthly"},
            }
        ],
    },
    {
        "createdAt": "2025-01-15T10:00:04Z",
        "run_id": "run_good_001",
        "tool_call_id": "call_001",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "tables": ["sales_2024", "sales_2023", "monthly_revenue"],
                    "message": "Found 3 relevant tables for 'sales data monthly'",
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T10:00:06Z",
        "run_id": "run_good_001",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_002",
                "name": "query_database",
                "arguments": {
                    "sql": "SELECT * FROM sales_2024 WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)"
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T10:00:08Z",
        "run_id": "run_good_001",
        "tool_call_id": "call_002",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "rows": [
                        {"month": "November", "total": 125000},
                        {"month": "December", "total": 180000},
                        {"month": "January", "total": 95000},
                    ],
                    "row_count": 3,
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T10:00:10Z",
        "run_id": "run_good_001",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "Here's the sales data for the last three months:\n\n"
                "- November: $125,000\n"
                "- December: $180,000\n"
                "- January: $95,000\n\n"
                "Total: $400,000. December was the strongest month.",
            }
        ],
    },
]

# -----------------------------------------------------------------------------
# SAMPLE 2: BAD - Agent queries a table NOT returned by search
# -----------------------------------------------------------------------------

BAD_QUERY = [
    {
        "role": "system",
        "content": "You are a database assistant. You help users query sales data. "
        "Always search for relevant tables before running queries. "
        "Only query tables that exist in the database.",
    },
    {
        "createdAt": "2025-01-15T11:00:00Z",
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Show me employee performance metrics.",
            }
        ],
    },
]

BAD_RESPONSE = [
    {
        "createdAt": "2025-01-15T11:00:02Z",
        "run_id": "run_bad_001",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_003",
                "name": "search_tables",
                "arguments": {"query": "employee performance"},
            }
        ],
    },
    {
        "createdAt": "2025-01-15T11:00:04Z",
        "run_id": "run_bad_001",
        "tool_call_id": "call_003",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "tables": ["employee_reviews", "performance_goals"],
                    "message": "Found 2 relevant tables for 'employee performance'",
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T11:00:06Z",
        "run_id": "run_bad_001",
        "role": "assistant",
        "content": [
            {
                "type": "tool_call",
                "tool_call_id": "call_004",
                "name": "query_database",
                "arguments": {
                    # BAD: employee_salaries was NOT returned by search_tables
                    "sql": "SELECT * FROM employee_salaries JOIN employee_reviews ON employee_salaries.emp_id = employee_reviews.emp_id"
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T11:00:08Z",
        "run_id": "run_bad_001",
        "tool_call_id": "call_004",
        "role": "tool",
        "content": [
            {
                "type": "tool_result",
                "tool_result": {
                    "error": "Access denied: table 'employee_salaries' not authorized",
                },
            }
        ],
    },
    {
        "createdAt": "2025-01-15T11:00:10Z",
        "run_id": "run_bad_001",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "I apologize, but I encountered an access error when trying to retrieve the data. "
                "It seems the employee_salaries table is restricted.",
            }
        ],
    },
]

# -----------------------------------------------------------------------------
# Convenience: All samples as a list for batch evaluation
# -----------------------------------------------------------------------------

ITEMS = [
    {
        "query": GOOD_QUERY,
        "response": GOOD_RESPONSE,
        "tool_definitions": TOOL_DEFINITIONS,
    },
    {
        "query": BAD_QUERY,
        "response": BAD_RESPONSE,
        "tool_definitions": TOOL_DEFINITIONS,
    },
]
