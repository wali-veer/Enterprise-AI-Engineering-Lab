"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    Batch Processing & Performance Benchmarking

Objective:
    Compare individual LLM request execution with asynchronous Batch API
    processing using the same workload.

    The utility measures execution characteristics including latency,
    processing time, token usage, cost, success rate, and workload behaviour.

Author:
    Veeresh Wali

Repository:
    https://github.com/wali-veer/Enterprise-AI-Engineering-Lab
===============================================================================
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from common.config import MODEL_NAME
from common.llm import invoke_model
from common.openai_client import client


console = Console()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROMPT_FILE = Path("prompts/08_batch_demo.txt")

BATCH_INPUT_FILE = Path("prompts/08_batch_input.jsonl")

POLL_INTERVAL = 2


# ---------------------------------------------------------------------------
# Prompt Loader
# ---------------------------------------------------------------------------

def load_prompts() -> list[str]:
    """
    Load the workload prompts.

    Each non-empty line represents one independent request.
    """

    return [
        line.strip()
        for line in PROMPT_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]


# ---------------------------------------------------------------------------
# Individual Execution
# ---------------------------------------------------------------------------

def execute_individual(
    prompts: list[str],
) -> dict:
    """
    Execute each prompt as an individual synchronous request.

    Returns
    -------
    dict
        Individual execution metrics.
    """

    console.print()
    console.rule(
        "[bold]Individual Execution[/bold]"
    )

    results = []

    workload_start = time.perf_counter()

    for index, prompt in enumerate(
        prompts,
        start=1,
    ):

        console.print(
            f"\nRequest {index}/{len(prompts)}"
        )

        request_start = time.perf_counter()

        try:

            result = invoke_model(
                model_name=MODEL_NAME,
                prompt=prompt,
            )

            elapsed = (
                time.perf_counter()
                - request_start
            )

            result["request"] = index
            result["status"] = "SUCCESS"
            result["request_latency"] = elapsed

            results.append(result)

            console.print(
                "[green]✓ Request completed successfully[/green]"
            )

        except Exception as ex:

            elapsed = (
                time.perf_counter()
                - request_start
            )

            results.append(
                {
                    "request": index,
                    "status": "FAILED",
                    "request_latency": elapsed,
                    "error": str(ex),
                }
            )

            console.print(
                f"[red]✗ Request failed: {ex}[/red]"
            )

    total_time = (
        time.perf_counter()
        - workload_start
    )

    successful = [
        result
        for result in results
        if result["status"] == "SUCCESS"
    ]

    total_input_tokens = sum(
        result["input_tokens"]
        for result in successful
    )

    total_output_tokens = sum(
        result["output_tokens"]
        for result in successful
    )

    total_tokens = sum(
        result["total_tokens"]
        for result in successful
    )

    total_cost = sum(
        result["cost"]
        for result in successful
    )

    latencies = [
        result["request_latency"]
        for result in successful
    ]

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0
    )

    return {
        "mode": "Individual",
        "results": results,
        "requests": len(prompts),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "total_time": total_time,
        "average_latency": average_latency,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_tokens,
        "cost": total_cost,
    }


# ---------------------------------------------------------------------------
# Batch Input Builder
# ---------------------------------------------------------------------------

def create_batch_input(
    prompts: list[str],
) -> Path:
    """
    Create the JSONL input file required by the OpenAI Batch API.
    """

    with BATCH_INPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        for index, prompt in enumerate(
            prompts,
            start=1,
        ):

            request = {
                "custom_id": f"request-{index}",
                "method": "POST",
                "url": "/v1/responses",
                "body": {
                    "model": MODEL_NAME,
                    "input": prompt,
                },
            }

            file.write(
                json.dumps(request)
                + "\n"
            )

    return BATCH_INPUT_FILE


# ---------------------------------------------------------------------------
# Batch Execution
# ---------------------------------------------------------------------------

def execute_batch(
    prompts: list[str],
) -> dict:
    """
    Execute the same workload using the OpenAI Batch API.

    The Batch API is asynchronous. The utility submits the workload,
    waits for completion, and collects batch-level metrics.
    """

    console.print()
    console.rule(
        "[bold]Batch API Execution[/bold]"
    )

    input_file = create_batch_input(
        prompts
    )

    console.print(
        "\nUploading batch input..."
    )

    upload_start = time.perf_counter()

    uploaded_file = client.files.create(
        file=input_file,
        purpose="batch",
    )

    upload_time = (
        time.perf_counter()
        - upload_start
    )

    console.print(
        "[green]✓ Batch input uploaded successfully[/green]"
    )

    console.print(
        f"Input File ID : {uploaded_file.id}"
    )

    # -----------------------------------------------------------------------
    # Batch submission
    # -----------------------------------------------------------------------

    console.print(
        "\nSubmitting batch..."
    )

    batch_total_start = time.perf_counter()

    submission_start = time.perf_counter()

    batch = client.batches.create(
        input_file_id=uploaded_file.id,
        endpoint="/v1/responses",
        completion_window="24h",
    )

    submission_time = (
        time.perf_counter()
        - submission_start
    )

    console.print(
        "[green]✓ Batch submitted successfully[/green]"
    )

    console.print(
        f"Batch ID      : {batch.id}"
    )

    # -----------------------------------------------------------------------
    # Poll until the batch reaches a terminal state.
    #
    # Only display status when the status changes. This keeps the output
    # concise while still showing the lifecycle of the batch.
    # -----------------------------------------------------------------------

    terminal_states = {
        "completed",
        "failed",
        "expired",
        "cancelled",
    }

    previous_status = None

    while batch.status not in terminal_states:

        if batch.status != previous_status:

            console.print(
                f"Batch Status  : {batch.status}"
            )

            previous_status = batch.status

        time.sleep(POLL_INTERVAL)

        batch = client.batches.retrieve(
            batch.id
        )

    # Display the final status if it has not already been displayed.
    if batch.status != previous_status:

        console.print(
            f"Batch Status  : {batch.status}"
        )

    batch_total_time = (
        time.perf_counter()
        - batch_total_start
    )

    batch_processing_time = max(
        batch_total_time - submission_time,
        0,
    )

    # -----------------------------------------------------------------------
    # Batch request counts
    # -----------------------------------------------------------------------

    request_counts = batch.request_counts

    completed = (
        request_counts.completed
        if request_counts
        else 0
    )

    failed = (
        request_counts.failed
        if request_counts
        else 0
    )

    total = (
        request_counts.total
        if request_counts
        else len(prompts)
    )

    # -----------------------------------------------------------------------
    # Batch usage
    # -----------------------------------------------------------------------

    usage = getattr(
        batch,
        "usage",
        None,
    )

    input_tokens = (
        usage.input_tokens
        if usage
        else 0
    )

    output_tokens = (
        usage.output_tokens
        if usage
        else 0
    )

    total_tokens = (
        usage.total_tokens
        if usage
        else 0
    )

    return {
        "mode": "Batch",
        "status": batch.status,
        "requests": total,
        "successful": completed,
        "failed": failed,
        "upload_time": upload_time,
        "submission_time": submission_time,
        "processing_time": batch_processing_time,
        "total_time": batch_total_time,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cost": None,
        "batch_id": batch.id,
    }


# ---------------------------------------------------------------------------
# Execution Comparison
# ---------------------------------------------------------------------------

def display_comparison(
    individual: dict,
    batch: dict,
) -> None:
    """
    Compare individual and Batch API execution.
    """

    console.print()

    console.rule(
        "[bold]Execution Comparison[/bold]"
    )

    table = Table(
        title="Individual vs Batch Execution"
    )

    table.add_column(
        "Metric"
    )

    table.add_column(
        "Individual",
        justify="right",
    )

    table.add_column(
        "Batch",
        justify="right",
    )

    table.add_row(
        "Requests",
        str(individual["requests"]),
        str(batch["requests"]),
    )

    table.add_row(
        "Successful",
        str(individual["successful"]),
        str(batch["successful"]),
    )

    table.add_row(
        "Failed",
        str(individual["failed"]),
        str(batch["failed"]),
    )

    table.add_row(
        "Execution Time",
        f"{individual['total_time']:.2f} sec",
        f"{batch['total_time']:.2f} sec",
    )

    table.add_row(
        "Input Tokens",
        str(individual["input_tokens"]),
        str(batch["input_tokens"]),
    )

    table.add_row(
        "Output Tokens",
        str(individual["output_tokens"]),
        str(batch["output_tokens"]),
    )

    table.add_row(
        "Total Tokens",
        str(individual["total_tokens"]),
        str(batch["total_tokens"]),
    )

    table.add_row(
        "Cost",
        f"${individual['cost']:.6f}",
        "See Batch pricing",
    )

    console.print(table)

    # -----------------------------------------------------------------------
    # Batch Timing Breakdown
    # -----------------------------------------------------------------------

    console.print()

    console.rule(
        "[bold]Batch Timing Breakdown[/bold]"
    )

    console.print(
        f"Individual Execution Time : "
        f"{individual['total_time']:.2f} sec"
    )

    console.print(
        f"Batch Submission Time     : "
        f"{batch['submission_time']:.2f} sec"
    )

    console.print(
        f"Batch Processing Time     : "
        f"{batch['processing_time']:.2f} sec"
    )

    console.print(
        f"Batch Total Elapsed Time  : "
        f"{batch['total_time']:.2f} sec"
    )


# ---------------------------------------------------------------------------
# Engineering Recommendation
# ---------------------------------------------------------------------------

def display_recommendation() -> None:
    """
    Display use-case-oriented engineering guidance.
    """

    console.print()

    console.rule(
        "[bold]Engineering Recommendation[/bold]"
    )

    recommendation = Panel.fit(
        "[bold]Key Engineering Insight[/bold]\n\n"
        "Individual and Batch execution are designed for different "
        "workload characteristics.\n\n"
        "Use individual execution when applications require immediate "
        "responses and request-level latency is important.\n\n"
        "Use Batch processing for asynchronous workloads where immediate "
        "responses are not required and many independent requests can "
        "be processed together.\n\n"
        "Neither execution model is universally better. The appropriate "
        "choice depends on the application's latency, workload, and "
        "processing requirements.",
        border_style="cyan",
    )

    console.print(
        recommendation
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Entry point for the batch processing benchmark.
    """

    prompts = load_prompts()

    console.print("\n" * 4)

    console.print(
        Panel.fit(
            "[bold cyan]"
            "Enterprise Batch Processing & Performance Benchmarking"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    console.print()

    console.print(
        "[green]✓ Workload loaded successfully[/green]"
    )

    console.print(
        f"Model            : {MODEL_NAME}"
    )

    console.print(
        f"Workload Size    : {len(prompts)} requests"
    )

    if not prompts:

        console.print(
            "[red]No prompts found.[/red]"
        )

        console.print("\n" * 4)

        return

    # -----------------------------------------------------------------------
    # Execute the same workload using both strategies.
    # -----------------------------------------------------------------------

    individual = execute_individual(
        prompts
    )

    batch = execute_batch(
        prompts
    )

    # -----------------------------------------------------------------------
    # Compare the two execution models.
    # -----------------------------------------------------------------------

    display_comparison(
        individual,
        batch,
    )

    display_recommendation()

    console.print("\n" * 4)


# ---------------------------------------------------------------------------
# Program Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()