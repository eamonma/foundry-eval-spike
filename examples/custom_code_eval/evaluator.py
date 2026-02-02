"""Length checker evaluator - a custom code-based evaluator."""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType


class LengthCheckerEvaluator:
    """Code-based evaluator that scores responses by length.

    Scoring:
    - 0.0: empty response
    - 0.5: < 20 characters
    - 1.0: >= 20 characters
    """

    CODE = '''
def grade(sample, item) -> float:
    """
    Score based on response length.
    - 0.0: empty
    - 0.5: < 20 chars
    - 1.0: >= 20 chars
    """
    response = item.get("response", "") if isinstance(item, dict) else ""
    if not response:
        return 0.0
    if len(response) < 20:
        return 0.5
    return 1.0
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
                "display_name": "Length Checker",
                "description": "Scores based on response length (no LLM)",
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
            "name": "length_check",
            "evaluator_name": self.name,
            "initialization_parameters": {
                "deployment_name": "unused",  # Not used by code evaluators
                "pass_threshold": pass_threshold,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        }
