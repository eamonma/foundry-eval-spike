"""Test data for custom LLM evaluator example."""

# Sample query-response pairs with varying quality
ITEMS = [
    {
        "query": "How do I reverse a list in Python?",
        "response": "Use list.reverse() or list[::-1]",
    },
    {
        "query": "How do I reverse a list in Python?",
        "response": "Python is a programming language.",
    },
    {
        "query": "What is 2+2?",
        "response": "4",
    },
]
