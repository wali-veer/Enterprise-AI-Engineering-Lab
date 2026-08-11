"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    Batch Processing & Performance Benchmarking

Objective:
    Demonstrate how enterprise AI applications process multiple LLM requests
    as a workload and measure execution performance, token usage, cost,
    latency, and throughput.

Author:
    Veeresh Wali

Repository:
    https://github.com/wali-veer/Enterprise-AI-Engineering-Lab
===============================================================================
"""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from common.config import MODEL_NAME
from common.llm import invoke_model


console = Console()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROMPT_FILE = Path("prompts/08_batch_demo.txt")

BATCH_SIZE = 5


# ---------------------------------------------------------------------------
# Prompt Loader
# ---------------------------------------------------------------------------

def load_prompts() -> list[str]:
    """
    Load the prompts used for the batch workload.

    Each non-empty line in the prompt file represents one request.
    """

    prompts = [
        line.strip()
        for line in PROMPT_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]

    return prompts[:BATCH_SIZE]


# ---------------------------------------------------------------------------
# Batch Processor
# ---------------------------------------------------------------------------

def process_batch(
    prompts: list[str],
) -> tuple[list[dict], float]:
    """
    Process a batch of prompts sequentially.

    Returns
    -------
    tuple
        Batch results and total execution time.
    """

    results = []

    batch_start = time.perf_counter()

    for index, prompt in enumerate(prompts, start=1):

        console.print(
            f"\n[bold]Request {index}/{len(prompts)}[/bold]"
        )

        request_start = time.perf_counter()

        try:

            result = invoke_model(
                model_name=MODEL_NAME,
                prompt=prompt,
            )

            request_latency = (
                time.perf_counter() - request_start
            )

            result["request"] = index
            result["status"] = "SUCCESS"
            result["request_latency"] = request_latency

            results.append(result)

            console.print(
                "[green]✓ Request completed successfully[/green]"
            )

        except Exception as ex:

            request_latency = (
                time.perf_counter() - request_start
            )

            results.append(
                {
                    "request": index,
                    "status": "FAILED",
                    "request_latency": request_latency,
                    "error": str(ex),
                }
            )

            console.print(
                f"[red]✗ Request failed: {ex}[/red]"
            )

    total_time = time.perf_counter() - batch_start

    return results, total_time


# ---------------------------------------------------------------------------
# Engineering Metrics
# ---------------------------------------------------------------------------

def display_metrics(
    results: list[dict],
    total_time: float,
) -> None:
    """
    Display request-level metrics and batch-level statistics.
    """

    console.print()

    console.rule(
        "[bold]Engineering Metrics[/bold]"
    )

    # -----------------------------------------------------------------------
    # Individual Request Metrics
    # -----------------------------------------------------------------------

    table = Table(
        title="Individual Request Metrics"
    )

    table.add_column(
        "Request",
        justify="center",
    )

    table.add_column(
        "Status",
        justify="center",
    )

    table.add_column(
        "Latency (sec)",
        justify="right",
    )

    table.add_column(
        "Input",
        justify="right",
    )

    table.add_column(
        "Output",
        justify="right",
    )

    table.add_column(
        "Cost ($)",
        justify="right",
    )

    for result in results:

        if result["status"] == "SUCCESS":

            table.add_row(
                str(result["request"]),
                result["status"],
                f"{result['request_latency']:.2f}",
                str(result["input_tokens"]),
                str(result["output_tokens"]),
                f"{result['cost']:.6f}",
            )

        else:

            table.add_row(
                str(result["request"]),
                result["status"],
                f"{result['request_latency']:.2f}",
                "-",
                "-",
                "-",
            )

    console.print(table)

    # -----------------------------------------------------------------------
    # Batch Statistics
    # -----------------------------------------------------------------------

    successful = [
        result
        for result in results
        if result["status"] == "SUCCESS"
    ]

    failed = [
        result
        for result in results
        if result["status"] == "FAILED"
    ]

    latencies = [
        result["request_latency"]
        for result in successful
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

    average_latency = (
        sum(latencies) / len(latencies)
        if latencies
        else 0
    )

    fastest_latency = (
        min(latencies)
        if latencies
        else 0
    )

    slowest_latency = (
        max(latencies)
        if latencies
        else 0
    )

    throughput = (
        len(successful) / total_time
        if total_time > 0
        else 0
    )

    console.print()

    console.rule(
        "[bold]Batch Statistics[/bold]"
    )

    console.print(
        f"Batch Size              : {len(results)}"
    )

    console.print(
        f"Successful Requests     : {len(successful)}"
    )

    console.print(
        f"Failed Requests         : {len(failed)}"
    )

    console.print(
        f"Total Execution Time    : {total_time:.2f} sec"
    )

    console.print(
        f"Average Request Latency : {average_latency:.2f} sec"
    )

    console.print(
        f"Fastest Request         : {fastest_latency:.2f} sec"
    )

    console.print(
        f"Slowest Request         : {slowest_latency:.2f} sec"
    )

    console.print(
        f"Throughput              : {throughput:.2f} requests/sec"
    )

    console.print(
        f"Total Input Tokens      : {total_input_tokens}"
    )

    console.print(
        f"Total Output Tokens     : {total_output_tokens}"
    )

    console.print(
        f"Total Tokens            : {total_tokens}"
    )

    console.print(
        f"Total Cost              : ${total_cost:.6f}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Entry point for the batch processing demonstration.
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
        "[green]✓ Batch workload loaded successfully[/green]"
    )

    console.print(
        f"Model            : {MODEL_NAME}"
    )

    console.print(
        f"Batch Size       : {len(prompts)}"
    )

    console.print()

    console.rule(
        "[bold]Batch Execution[/bold]"
    )

    if not prompts:

        console.print(
            "[red]No prompts found in the batch workload.[/red]"
        )

        console.print("\n" * 4)

        return

    results, total_time = process_batch(prompts)

    display_metrics(
        results,
        total_time,
    )

    console.print()

    console.rule(
        "[bold]Engineering Recommendation[/bold]"
    )

    recommendation = Panel.fit(
        "[bold]Key Engineering Insight[/bold]\n\n"
        "AI workloads should be measured at both the request and\n"
        "workload level.\n\n"
        "Individual metrics show request behaviour, while batch\n"
        "statistics reveal overall latency, throughput, token\n"
        "consumption, and cost.",
        border_style="cyan",
    )

    console.print(recommendation)

    console.print("\n" * 4)


# ---------------------------------------------------------------------------
# Program Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()