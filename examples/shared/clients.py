"""Client initialization and configuration."""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

ENDPOINT = os.environ["AZURE_EXISTING_AIPROJECT_ENDPOINT"]
DEFAULT_JUDGE_MODEL = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-5-mini")


@contextmanager
def get_clients():
    """Yields (project_client, openai_client)."""
    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=ENDPOINT, credential=credential) as project_client:
            yield project_client, project_client.get_openai_client()
