"""Evaluation execution utilities."""

import time


def wait_for_completion(client, eval_id: str, run_id: str, poll_interval: int = 3):
    """Polls until eval run completes. Returns (run, output_items)."""
    while True:
        run = client.evals.runs.retrieve(run_id=run_id, eval_id=eval_id)
        if run.status in ("completed", "failed"):
            output_items = list(
                client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_id)
            )
            return run, output_items
        print(f"  Status: {run.status}")
        time.sleep(poll_interval)


def wait_for_evaluator(project_client, name: str, expected_version: str, max_wait: int = 60):
    """Poll until the evaluator version is available."""
    print(f"  Waiting for {name} v{expected_version}...")
    start = time.time()
    while time.time() - start < max_wait:
        try:
            versions = list(project_client.evaluators.list_versions(name))
            if expected_version in [v.version for v in versions]:
                print(f"  ✓ {name} v{expected_version} available")
                return True
        except Exception:
            pass
        time.sleep(2)
    print(f"  WARNING: {name} not found after {max_wait}s")
    return False


def print_results(run, output_items):
    """Prints formatted evaluation results."""
    print(f"\n=== Results ({run.status}) ===\n")
    for i, item in enumerate(output_items):
        print(f"[{i+1}] {item.datasource_item}")
        for r in item.results:
            if r.sample and isinstance(r.sample, dict) and "error" in r.sample:
                print(f"    {r.name}: ERROR - {r.sample['error']['message'][:100]}...")
            else:
                print(
                    f"    {r.name}: {r.score} {'✓' if r.passed else '✗'} - {r.reason or ''}"
                )
        print()
    print(f"Report: {run.report_url}\n")
