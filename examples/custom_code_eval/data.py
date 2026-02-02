"""Test data for custom code evaluator example."""

# Sample responses with varying lengths to test the evaluator
ITEMS = [
    {"query": "Say something", "response": ""},  # empty → 0.0
    {"query": "Say something", "response": "Hi"},  # short → 0.5
    {"query": "Say something", "response": "This is a longer response with more content."},  # long → 1.0
]
