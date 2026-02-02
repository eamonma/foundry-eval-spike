---
title: General Purpose Evaluators for Generative AI
titleSuffix: Microsoft Foundry
description: Learn about general-purpose evaluators for generative AI, including coherence, fluency, and question-answering composite evaluation.
monikerRange: 'foundry'
ai-usage: ai-assisted
author: lgayhardt
ms.author: lagayhar
ms.reviewer: changliu2
ms.date: 11/18/2025
ms.service: azure-ai-foundry
ms.topic: reference
ms.custom:
  - build-aifnd
  - build-2025
---

# General purpose evaluators

[!INCLUDE [version-banner](../../includes/version-banner.md)]

AI systems might generate textual responses that are incoherent, or lack the general writing quality beyond minimum grammatical correctness. To address these issues, Microsoft Foundry supports evaluating:

- [Coherence](#coherence)
- [Fluency](#fluency)

[!INCLUDE [evaluation-preview](../../includes/evaluation-preview.md)]



## Coherence

`CoherenceEvaluator` measures the logical and orderly presentation of ideas in a response, which allows the reader to easily follow and understand the writer's train of thought. A *coherent* response directly addresses the question with clear connections between sentences and paragraphs, using appropriate transitions and a logical sequence of ideas. Higher scores mean better coherence.


## Fluency

`FluencyEvaluator` measures the effectiveness and clarity of written communication. This measure focuses on grammatical accuracy, vocabulary range, sentence complexity, coherence, and overall readability. It assesses how smoothly ideas are conveyed and how easily the reader can understand the text.



## Example using coherence and fluency

```python
from dotenv import load_dotenv
import json
import os
import time
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
load_dotenv()

def main() -> None:
    endpoint = os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini

    with DefaultAzureCredential() as credential:
        with AIProjectClient(
            endpoint=endpoint, credential=credential
        ) as project_client:
            print("Creating an OpenAI client from the AI Project client")

            client = project_client.get_openai_client()

            data_source_config = {
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}, "response": {"type": "string"}},
                    "required": [],
                },
                "include_sample_schema": True,
            }

            testing_criteria = [
                {
                    "type": "azure_ai_evaluator",
                    "name": "coherence",
                    "evaluator_name": "builtin.coherence",
                    "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                    "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
                },
                {
                    "type": "azure_ai_evaluator",
                    "name": "fluency",
                    "evaluator_name": "builtin.fluency",
                    "initialization_parameters": {"deployment_name": f"{model_deployment_name}"},
                    "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
                }
            ]

            print("Creating Eval Group")
            eval_object = client.evals.create(
                name="Test Coherence Evaluator with inline data",
                data_source_config=data_source_config,
                testing_criteria=testing_criteria,
            )
            print(f"Eval Group created")

            print("Get Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Run Response:")
            pprint(eval_object_response)

            # Sample inline data
            success_query = "What is the capital/major city of France?"
            success_response = "The capital/major city of France is Paris."

            # Failure example - incoherent response
            failure_query = "What is the capital/major city of France?"
            failure_response = "France capital/major city is... well, the city where government sits is Paris but no wait, Lyon is bigger actually maybe Rome? The French people live in many cities but the main one, I think it's definitely Paris or maybe not, depends on what you mean by capital/major city."

            print("Creating Eval Run with Inline Data")
            eval_run_object = client.evals.runs.create(
                eval_id=eval_object.id,
                name="inline_data_run",
                metadata={"team": "eval-exp", "scenario": "inline-data-v1"},
                data_source=CreateEvalJSONLRunDataSourceParam(
                    type="jsonl",
                    source=SourceFileContent(
                        type="file_content",
                        content=[
                            # Success example - coherent response
                            SourceFileContentContent(item={"query": success_query, "response": success_response}),
                            # Failure example - incoherent response
                            SourceFileContentContent(item={"query": failure_query, "response": failure_response}),
                        ],
                    ),
                ),
            )

            print(f"Eval Run created")
            pprint(eval_run_object)

            print("Get Eval Run by Id")
            eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
            print("Eval Run Response:")
            pprint(eval_run_response)

            print("\n\n----Eval Run Output Items----\n\n")

            while True:
                run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
                if run.status == "completed" or run.status == "failed":
                    output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                    pprint(output_items)
                    print(f"Eval Run Status: {run.status}")
                    print(f"Eval Run Report URL: {run.report_url}")
                    break
                time.sleep(5)
                print("Waiting for eval run to complete...")


if __name__ == "__main__":
    main()
```

For more details, see the [complete working sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_coherence.py).


## Related content

- [How to run batch evaluation on a dataset](../../how-to/develop/evaluate-sdk.md#local-evaluation-on-test-datasets-using-evaluate)  
- [How to run batch evaluation on a target](../../how-to/develop/evaluate-sdk.md#local-evaluation-on-a-target)
