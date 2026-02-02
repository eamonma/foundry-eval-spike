"""Helpfulness judge evaluator - a custom LLM-based evaluator."""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType


class HelpfulnessJudgeEvaluator:
    """LLM-based evaluator that judges response helpfulness.

    Uses an LLM to score responses on a 1-5 scale based on how
    helpfully and correctly they answer the query.
    """

    PROMPT = """
You are a Helpfulness Evaluator.

Evaluate whether the response helpfully and correctly answers the query.

### Input:
Query: {{query}}
Response: {{response}}

### Scoring Scale (1-5):
5 = Excellent. Fully answers the query with accurate, helpful information.
4 = Good. Mostly answers the query with minor gaps.
3 = Partial. Addresses the query but missing key information.
2 = Poor. Barely relevant or mostly unhelpful.
1 = Fail. Does not answer the query or is incorrect.

### Output Format (JSON):
{"result": <integer 1-5>, "reason": "<brief explanation>"}
"""

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
                "display_name": "Helpfulness Judge",
                "description": "Evaluates if response helpfully answers the query",
                "definition": {
                    "type": EvaluatorDefinitionType.PROMPT,
                    "prompt_text": self.PROMPT,
                    "init_parameters": {
                        "type": "object",
                        "properties": {
                            "deployment_name": {"type": "string"},
                            "threshold": {"type": "number"},
                        },
                        "required": ["deployment_name", "threshold"],
                    },
                    "data_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "response": {"type": "string"},
                        },
                        "required": ["query", "response"],
                    },
                    "metrics": {
                        "helpfulness": {
                            "type": "ordinal",
                            "desirable_direction": "increase",
                            "min_value": 1,
                            "max_value": 5,
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

    def get_testing_criterion(self, deployment_name: str, threshold: int = 3):
        """Return the testing criterion config for this evaluator."""
        return {
            "type": "azure_ai_evaluator",
            "name": "helpfulness",
            "evaluator_name": self.name,
            "initialization_parameters": {
                "deployment_name": deployment_name,
                "threshold": threshold,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        }
