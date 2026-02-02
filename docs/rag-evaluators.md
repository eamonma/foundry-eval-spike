---
title: Retrieval-Augmented Generation (RAG) Evaluators for Generative AI
titleSuffix: Microsoft Foundry
description: Learn about Retrieval-Augmented Generation evaluators for assessing relevance, groundedness, and response completeness in generative AI systems.
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

# Retrieval-Augmented Generation (RAG) evaluators

[!INCLUDE [version-banner](../../includes/version-banner.md)]

A Retrieval-Augmented Generation (RAG) system tries to generate the most relevant answer consistent with grounding documents in response to a user's query. A user's query triggers a search retrieval in the corpus of grounding documents to provide grounding context for the AI model to generate a response.

[!INCLUDE [evaluation-preview](../../includes/evaluation-preview.md)]



| Evaluator | Best practice | Use when | Purpose | Inputs | Output |
|--|--|--|--|--|--|
| Document Retrieval | Process evaluation | Retrieval quality is a bottleneck for your RAG, and you have query relevance labels (ground truth) for precise search quality metrics for debugging and parameter optimization | Measures search quality metrics (Fidelity, NDCG, XDCG, Max Relevance, Holes) by comparing retrieved documents against ground truth labels | `retrieval_ground_truth`, `retrieval_documents` | Composite: Fidelity, NDCG, XDCG, Max Relevance, Holes (with Pass/Fail) |
| Retrieval | Process evaluation | You want to assess textual quality of retrieved context, but you don't have ground truths | Measures how relevant the retrieved context chunks are to addressing a query using an LLM judge | Query, Context | Binary: Pass/Fail based on threshold (1-5 scale) |
| Groundedness | System evaluation |  You want a well-rounded groundedness definition that works with agent inputs, and bring your own GPT models as the LLM-judge | Measures how well the generated response aligns with the given context without fabricating content (precision aspect) | Query, Context, Response | Binary: Pass/Fail based on threshold (1-5 scale) |
| Groundedness Pro (preview)| System evaluation | You want a strict groundedness definition powered by Azure AI Content Safety and use our service model | Detects if the response is strictly consistent with the context using the Azure AI Content Safety service | Query, Context, Response | Binary: True/False |
| Relevance | System evaluation | You want to assess how well the RAG response addresses the query but don't have ground truths | Measures the accuracy, completeness, and direct relevance of the response to the query | Query, Response | Binary: Pass/Fail based on threshold (1-5 scale) |
| Response Completeness | System evaluation | You want to ensure the RAG response doesn't miss critical information (recall aspect) from your ground truth | Measures how completely the response covers the expected information compared to ground truth | Response, Ground truth | Binary: Pass/Fail based on threshold (1-5 scale) |


Think about *groundedness* and *response completeness* as:

- Groundedness focuses on the *precision* aspect of the response. It doesn't contain content outside of the grounding context.
- Response completeness focuses on the *recall* aspect of the response. It doesn't miss critical information compared to the expected response or ground truth.



## System evaluation

System evaluation focuses on assessing the relevance, groundedness, and response completeness of the generated response in RAG systems. These evaluators help ensure that the AI-generated content is accurate, relevant, and complete based on the provided context and user query.

Examples

- [Groundedness sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_groundedness.py)
- [Relevance sample](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations/agentic_evaluators/sample_relevance.py)
- For the Groundedness Pro response completeness sample, see [system and process evaluation example](#example-of-system-and-process-evaluation).

## Process evaluation

Process evaluation assesses the quality of the document retrieval process in RAG systems. The retrieval step is crucial for providing relevant context to the language model, so evaluating its effectiveness ensures the RAG system generates accurate and contextually appropriate responses.

Examples:

- [Document retrieval example](#document-retrieval-example)
- For a retrieval sample, see [system and process evaluation example](#example-of-system-and-process-evaluation).

## Evaluator model support for AI-assisted evaluators

For AI-assisted evaluators, use Azure OpenAI or OpenAI [reasoning models](../../../ai-services/openai/how-to/reasoning.md) and non-reasoning models for the LLM-judge depending on the evaluators. For complex evaluation that requires refined reasoning, use a strong reasoning model like `gpt-5-mini` with a balance of reasoning performance, cost, and efficiency.

## Example of system and process evaluation

> [!NOTE]
> Inline datasource is not supported for virtual network.

```python
from dotenv import load_dotenv
import os
import json
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
                "properties": {
                    "context": {"type": "string"},
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "ground_truth": {"type": "string"},
                },
                "required": ["response"] # see example below for specific input requirements
            },
            "include_sample_schema": True,
        }

        testing_criteria = [
            # System evaluation criteria
            {
                "type": "azure_ai_evaluator",
                "name": "groundedness",
                "evaluator_name": "builtin.groundedness",
                "initialization_parameters": {
                    "deployment_name": f"{model_deployment_name}",
                    # "is_reasoning_model": True # if you use an AOAI reasoning model
                },
                "data_mapping": {
                    "context": "{{item.context}}",
                    "query": "{{item.query}}",
                    "response": "{{item.response}}"
                },
            },
            {
                "type": "azure_ai_evaluator",
                "name": "relevance",
                "evaluator_name": "builtin.relevance",
                "initialization_parameters": {
                    "deployment_name": f"{model_deployment_name}",
                    # "is_reasoning_model": True # if you use an AOAI reasoning model        
                },
                "data_mapping": {
                    "query": "{{item.query}}",
                    "response": "{{item.response}}",
                },
            },
            {
                "type": "azure_ai_evaluator",
                "name": "response_completeness",
                "evaluator_name": "builtin.response_completeness",
                "initialization_parameters": {
                    "deployment_name": f"{model_deployment_name}",
                    # "is_reasoning_model": True # if you use an AOAI reasoning model        
                },
                "data_mapping": {
                    "response": "{{item.response}}",
                    "ground_truth": "{{item.ground_truth}}",
                },
            },
            # Process evaluation criteria
            {
                "type": "azure_ai_evaluator",
                "name": "retrieval",
                "evaluator_name": "builtin.retrieval",
                "initialization_parameters": {
                    "deployment_name": f"{model_deployment_name}",
                    # "is_reasoning_model": True # if you use an AOAI reasoning model
                },
                "data_mapping": {
                    "context": "{{item.context}}",
                    "query": "{{item.query}}",
                },
            },
        ]

        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="Test Groundedness Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        query = "What is the cheapest available tent of Contoso Outdoor?"
        context = (
            "Contoso Outdoor is a leading retailer specializing in outdoor gear and equipment. "
            "Contoso Product Catalog: 1. tent A - $99.99, lightweight 2-person tent; 2. tent B - $149.99, 4-person family tent; tent C - $199.99, durable 6-person expedition tent."
        )
        response = "The cheapest available tent is tent A, priced at $99.99."
        ground_truth = "The cheapest available tent is tent A, priced at $99.99."

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
                        SourceFileContentContent(
                            item={
                                "context": context,
                                "response": response,
                                "query": query,
                                "ground_truth": ground_truth
                            }
                        )
                    ]
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

```


## Document retrieval



Because of its upstream role in RAG, the retrieval quality is important. If the retrieval quality is poor and the response requires corpus-specific knowledge, there's less chance your language model gives you a satisfactory answer. The most precise measurement is to use the `document_retrieval` evaluator to evaluate retrieval quality and optimize your search parameters for RAG.


- Document retrieval evaluator measures how well the RAG retrieves the correct documents from the document store. As a composite evaluator useful for RAG scenario with ground truth, it computes a list of useful search quality metrics for debugging your RAG pipelines:

  | Metric | Category | Description |
  |--|--|--|
  | Fidelity | Search Fidelity | How well the top n retrieved chunks reflect the content for a given query: number of good documents returned out of the total number of known good documents in a dataset |
  | NDCG | Search NDCG | How good are the rankings to an ideal order where all relevant items are at the top of the list |
  | XDCG | Search XDCG | How good the results are in the top-k documents regardless of scoring of other index documents |
  | Max Relevance N | Search Max Relevance | Maximum relevance in the top-k chunks |
  | Holes | Search Label Sanity | Number of documents with missing query relevance judgments, or ground truth |



- To optimize your RAG in a scenario called *parameter sweep*, you can use these metrics to calibrate the search parameters for the optimal RAG results. Generate different retrieval results for various search parameters such as search algorithms (vector, semantic), top_k, and chunk sizes you're interested in testing. Then use `document_retrieval` to find the search parameters that yield the highest retrieval quality.


### Document retrieval example



```python

from dotenv import load_dotenv
import os
import json
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

endpoint = os.environ.get(
    "AZURE_AI_PROJECT_ENDPOINT", ""
)  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

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
                "properties": {
                    "retrieved_documents": {"type": "array", "items": {"type": "object"}},
                    "retrieval_ground_truth": {"type": "array", "items": {"type": "object"}}
                },
                "required": ["retrieved_documents", "retrieval_ground_truth"],
            },
            "include_sample_schema": True,
        }

        testing_criteria = [
            {
                "type": "azure_ai_evaluator",
                "name": "document_retrieval",
                "evaluator_name": "builtin.document_retrieval",
                "initialization_parameters": {
                    # The min and max of the retrieval_ground_truth scores are required inputs to document retrieval evaluator
                    "ground_truth_label_min": 1, "ground_truth_label_max": 5
                },
                "data_mapping": {
                    "retrieval_ground_truth": "{{item.retrieval_ground_truth}}", 
                    "retrieval_documents": "{{item.retrieved_documents}}"
                },
            }
        ]

        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="Test Task Navigation Efficiency Evaluator with inline data",
            data_source_config=data_source_config,
            testing_criteria=testing_criteria,
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)
        

        # Score each retrieval from a user's query by your human experts or LLM-judges such as relevance.
        retrieval_ground_truth = [
            {
                "document_id": "1",
                "query_relevance_label": 4
            },
            {
                "document_id": "2",
                "query_relevance_label": 2
            },
            {
                "document_id": "3",
                "query_relevance_label": 3
            },
            {
                "document_id": "4",
                "query_relevance_label": 1
            },
            {
                "document_id": "5",
                "query_relevance_label": 0
            },
        ]
        
        # These relevance scores for each retrieval chunk come from your search retrieval system
        retrieved_documents = [
            {
                "document_id": "2",
                "relevance_score": 45.1
            },
            {
                "document_id": "6",
                "relevance_score": 35.8
            },
            {
                "document_id": "3",
                "relevance_score": 29.2
            },
            {
                "document_id": "5",
                "relevance_score": 25.4
            },
            {
                "document_id": "7",
                "relevance_score": 18.8
            },
        ]

        print("Creating Eval Run with Inline Data")
        eval_run_object = client.evals.runs.create(
            eval_id=eval_object.id,
            name="document_retrieval_inline_data_run",
            metadata={"team": "eval-exp", "scenario": "inline-data-v1"},
            data_source=CreateEvalJSONLRunDataSourceParam(
                type="jsonl",
                source=SourceFileContent(
                    type="file_content",
                    content=[
                        SourceFileContentContent(
                            item={"retrieval_ground_truth": retrieval_ground_truth, "retrieved_documents": retrieved_documents}
                        )
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
```


### Document retrieval output

All numerical scores have `high_is_better=True`, except for `holes` and `holes_ratio`, which have `high_is_better=False`. With a numerical threshold (default of 3), the evaluator outputs *pass* if the score is greater than or equal to the threshold, or *fail* otherwise.



```python
{
    "ndcg@3": 0.6461858173,
    "xdcg@3": 37.7551020408,
    "fidelity": 0.0188438199,
    "top1_relevance": 2,
    "top3_max_relevance": 2,
    "holes": 30,
    "holes_ratio": 0.6000000000000001,
    "holes_higher_is_better": False,
    "holes_ratio_higher_is_better": False,
    "total_retrieved_documents": 50,
    "total_groundtruth_documents": 1565,
    "ndcg@3_result": "pass",
    "xdcg@3_result": "pass",
    "fidelity_result": "fail",
    "top1_relevance_result": "fail",
    "top3_max_relevance_result": "fail",
    # Omitting more fields ...
}
```



## Related content



- [More examples for quality evaluators](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations)
- [How to run agent evaluation](../../how-to/develop/agent-evaluate-sdk.md)
- [How to run cloud evaluation](../../how-to/develop/cloud-evaluation.md)
- [How to optimize agentic RAG](https://aka.ms/optimize-agentic-rag-blog)

