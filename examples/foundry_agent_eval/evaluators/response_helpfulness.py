"""Response Helpfulness Evaluator - LLM-based (prompt).

Judges whether the agent provided a helpful response that goes beyond
just stating raw data. Uses an LLM to evaluate subjective quality.

NOTE: LLM (prompt) evaluators work with BOTH 'azure_ai_responses' and 'custom'
data sources, unlike code evaluators which only work with 'custom'.
"""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType


class ResponseHelpfulnessEvaluator:
    """LLM-based evaluator that judges response helpfulness."""

    PROMPT = """
You are evaluating an AI weather assistant's response.

User Query: {{query}}

Agent Response: {{response}}

Evaluate whether the agent provided a HELPFUL response that goes beyond just
stating raw data. A helpful response might include:
- Practical advice (e.g., "bring an umbrella")
- Temperature conversions
- Context about conditions
- Offers for follow-up information

### Scoring Scale (1-5):
5 = Excellent. Response provides rich context, practical advice, and offers follow-up.
4 = Good. Response includes some helpful context beyond raw data.
3 = Adequate. Response answers the question but adds little value.
2 = Minimal. Response barely addresses the query or is very terse.
1 = Poor. Response is unhelpful, confusing, or doesn't answer the query.

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
                "display_name": "Response Helpfulness Judge",
                "description": "Judges if the agent response provides helpful context",
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
        """Return the testing criterion config for this evaluator.

        When used with azure_ai_responses, include data_mapping for the
        auto-extracted fields.
        """
        return {
            "type": "azure_ai_evaluator",
            "name": "response_helpfulness",
            "evaluator_name": self.name,
            "initialization_parameters": {
                "deployment_name": deployment_name,
                "threshold": threshold,
            },
            "data_mapping": {
                "query": "{{last_query_text}}",
                "response": "{{response_text}}",
            },
        }
