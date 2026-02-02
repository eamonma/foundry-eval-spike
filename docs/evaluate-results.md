---
title: See Evaluation Results in Microsoft Foundry portal
titleSuffix: Microsoft Foundry
description: See and analyze AI model evaluation results in Microsoft Foundry portal. Learn to view performance metrics, compare results, and interpret evaluation data for model optimization.
ms.service: azure-ai-foundry
ms.custom:
  - ignite-2023
  - build-2024
  - ignite-2024
ms.topic: how-to
ms.date: 12/22/2025
ms.reviewer: dlozier
ms.author: lagayhar
author: lgayhardt
monikerRange: 'foundry'
ai-usage: ai-assisted
---

# See evaluation results in the Microsoft Foundry portal

[!INCLUDE [version-banner](../includes/version-banner.md)]

Learn how to see evaluation results in the Microsoft Foundry portal. View and interpret AI model evaluation data, performance metrics, and quality assessments. Access results from flows, playground sessions, and SDK to make data-driven decisions.

After visualizing your evaluation results, examine them thoroughly. View individual results, compare them across multiple evaluation runs, and identify trends, patterns, and discrepancies to gain insights into your AI system's performance under various conditions.

In this article, you learn to:

- Locate and open evaluation runs.
- View aggregate and sample-level metrics.
- Compare results across runs.
- Interpret metric categories and calculations.
- Troubleshoot missing or partial metrics.

## See your evaluation results



In Microsoft Foundry, the concept of group runs is introduced. You can create multiple runs within a group that share common characteristics, such as metrics and datasets, to make comparison easier. Once you run an evaluation, locate the group on the **Evaluation** page, which contains a list of group evaluations and associated meta data, such as the number of targets and the last modified date.  

Select a group run to review group details, including each run and high-level metrics, such as run duration, tokens, and evaluator scores, for each run within that group.

By selecting a run within this group, you can also drill in to view the row detailed data for that particular run.  

Select **Learn more about metrics** for definitions and formulas.




### Evaluation Runs Results and Pass Rate

You can view each run within a group on the Evaluation Runs and Results Pass Rate page. This view shows the run, target, status,  run duration, tokens, and pass rate for each evaluator chosen.  

If you would like to cancel runs, you can do so by selecting each run and clicking “cancel runs” at the top of the table.




### Evaluation Run Data

To view the turn by turn data for individual runs, select the name of the run. This provides a view that allows you to see evaluation results by turn against each evaluator used.


## Compare the evaluation results



To facilitate a comprehensive comparison between two or more runs, you can select the desired runs and initiate the process.

1. Select two or more runs in the evaluation detail page.
1. Select **Compare**.

It generates a side-by-side comparison view for all selected runs.

The comparison is computed based on statistic t-testing, which provides more sensitive and reliable results for you to make decisions. You can use different functionalities of this feature:

- Baseline comparison: By setting a baseline run, you can identify a reference point against which to compare the other runs. You can see how each run deviates from your chosen standard.
- Statistic t-testing assessment: Each cell provides the stat-sig results with different color codes. You can also hover on the cell to get the sample size and p-value.  

|Legend | Definition|
|--|--|
| ImprovedStrong | Highly stat-sig (p<=0.001) and moved in the desired direction |
| ImprovedWeak  | Stat-sig (0.001<p<=0.05) and moved in the desired direction |
| DegradedStrong | Highly stat-sig (p<=0.001) and moved in the wrong direction |
| DegradedWeak | Stat-sig (0.001<p<=0.05) and moved in the wrong direction |
| ChangedStrong | Highly stat-sig (p<=0.001) and desired direction is neutral |
| ChangedWeak | Stat-sig (0.001<p<=0.05) and desired direction is neutral |
| Inconclusive | Too few examples, or p>=0.05 |

> [!NOTE]
> The comparison view won't be saved. If you leave the page, you can reselect the runs and select **Compare** to regenerate the view.



## Understand the built-in evaluation metrics

Understanding the built-in metrics is essential for assessing the performance and effectiveness of your AI application. By learning about these key measurement tools, you can interpret the results, make informed decisions, and fine-tune your application to achieve optimal outcomes.

To learn more, see [What are evaluators?](../concepts/observability.md#what-are-evaluators).

## Troubleshooting

| Symptom | Possible cause | Action |
|---------|----------------|-------|
| Run stays pending | High service load or queued jobs | Refresh, verify quota, and resubmit if prolonged |
| Metrics missing | Not selected at creation | Rerun and select required metrics |
| All safety metrics zero | Category disabled or unsupported model | Confirm model and metric support matrix |
| Groundedness unexpectedly low | Retrieval/context incomplete | Verify context construction / retrieval latency |

## Related content

- Improve low metrics with prompt iteration or [fine-tuning](../concepts/fine-tuning-overview.md).
- [Run evaluations in the cloud with the Microsoft Foundry SDK](./develop/cloud-evaluation.md).

Learn how to evaluate your generative AI applications:

- [Evaluate your generative AI apps with the Foundry portal or SDK](../how-to/evaluate-generative-ai-app.md).
- [Create evaluations with OpenAI evaluation graders in Azure OpenAI Hub](../openai/how-to/evaluations.md).
