"""Response Length Evaluator - CODE-based (no LLM).

Checks if the agent response meets minimum length requirements.
This is a deterministic evaluator that doesn't use an LLM judge.

NOTE: Code evaluators only work with 'custom' data source (simple strings),
NOT with 'azure_ai_responses' data source.
"""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType


class ResponseLengthEvaluator:
    """Code-based evaluator that checks response length."""

    # The Python code that runs during evaluation
    CODE = '''
def grade(sample, item) -> float:
    """
    Check if the agent response meets minimum length requirements.
    Returns: 1.0 (>=50 chars), 0.5 (>=20 chars), 0.0 (<20 chars)
    """
    response = item.get("response", "") if isinstance(item, dict) else ""
    if not response:
        return 0.0
    length = len(response)
    if length >= 50:
        return 1.0
    elif length >= 20:
        return 0.5
    else:
        return 0.0
'''

    def __init__(self, name: str):
        """Initialize with a unique evaluator name."""
        self.name = name
        self._evaluator = None

    def create(self, project_client):
        """Register the evaluator with the project."""
        self._evaluator = project_client.evaluators.create_version(
            name=self.name,
            evaluator_version={
                "name": self.name,
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "Response Length Check",
                "description": "Checks if agent response meets minimum length requirements",
                "definition": {
                    "type": EvaluatorDefinitionType.CODE,
                    "code_text": self.CODE,
                    "init_parameters": {
                        "type": "object",
                        "properties": {
                            "deployment_name": {"type": "string"},
                            "pass_threshold": {"type": "number"},
                        },
                        "required": ["deployment_name", "pass_threshold"],
                    },
                    "data_schema": {
                        "type": "object",
                        "properties": {
                            "item": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "response": {"type": "string"},
                                },
                            },
                        },
                        "required": ["item"],
                    },
                    "metrics": {
                        "result": {
                            "type": "ordinal",
                            "desirable_direction": "increase",
                            "min_value": 0.0,
                            "max_value": 1.0,
                        }
                    },
                },
            },
        )
        return self._evaluator

    def delete(self, project_client):
        """Remove the evaluator from the project."""
        if self._evaluator:
            project_client.evaluators.delete_version(
                name=self._evaluator.name, version=self._evaluator.version
            )

    @property
    def version(self):
        """Return the evaluator version."""
        return self._evaluator.version if self._evaluator else None

    def get_testing_criterion(self, pass_threshold: float = 0.5):
        """Return the testing criterion config for this evaluator."""
        return {
            "type": "azure_ai_evaluator",
            "name": "response_length",
            "evaluator_name": self.name,
            "initialization_parameters": {
                "deployment_name": "unused",  # Not used by code evaluators
                "pass_threshold": pass_threshold,
            },
        }
