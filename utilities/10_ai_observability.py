"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    AI Observability & Engineering Telemetry

Objective:
    Demonstrate how AI applications capture request, performance, token,
    cost, and reliability telemetry and convert that telemetry into
    actionable engineering health signals.

Author:
    Veeresh Wali

Repository:
    https://github.com/wali-veer/Enterprise-AI-Engineering-Lab
===============================================================================
"""

from pathlib import Path
from statistics import mean

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from common.config import MODEL_NAME
from common.llm import invoke_model


console = Console()

PROMPT_FILE = Path("prompts/10_observability_demo.txt")
MAX_REQUESTS = 5

# ---------------------------------------------------------------------------
# Demonstration thresholds
#
# These are demonstration thresholds for this utility, not universal
# production SRE standards. Production thresholds should be derived from
# workload-specific SLOs and historical baselines.
# ---------------------------------------------------------------------------

AVG_LATENCY_WARNING = 10.0
AVG_LATENCY_CRITICAL = 20.0

REQUEST_LATENCY_WARNING = 15.0
REQUEST_LATENCY_CRITICAL = 25.0

SUCCESS_RATE_WARNING = 99.0
SUCCESS_RATE_CRITICAL = 95.0

ERROR_RATE_WARNING = 1.0
ERROR_RATE_CRITICAL = 5.0


# ---------------------------------------------------------------------------
# Prompt Loader
# ---------------------------------------------------------------------------

def load_prompts() -> list[str]:
    """Load the observability workload prompts."""

    content = PROMPT_FILE.read_text(encoding="utf-8").strip()

    return [
        block.strip()
        for block in content.split("\n---\n")
        if block.strip()
    ]


# ---------------------------------------------------------------------------
# Threshold Classification
# ---------------------------------------------------------------------------

def classify_latency(latency: float) -> tuple[str, str]:
    """Classify an individual request latency."""

    if latency >= REQUEST_LATENCY_CRITICAL:
        return "CRITICAL", "bold red"

    if latency >= REQUEST_LATENCY_WARNING:
        return "WARNING", "yellow"

    return "HEALTHY", "green"


def classify_average_latency(latency: float) -> tuple[str, str]:
    """Classify aggregate average latency."""

    if latency >= AVG_LATENCY_CRITICAL:
        return "CRITICAL", "bold red"

    if latency >= AVG_LATENCY_WARNING:
        return "WARNING", "yellow"

    return "HEALTHY", "green"


def classify_success_rate(rate: float) -> tuple[str, str]:
    """Classify workload success rate."""

    if rate < SUCCESS_RATE_CRITICAL:
        return "CRITICAL", "bold red"

    if rate < SUCCESS_RATE_WARNING:
        return "WARNING", "yellow"

    return "HEALTHY", "green"


def classify_error_rate(rate: float) -> tuple[str, str]:
    """Classify workload error rate."""

    if rate > ERROR_RATE_CRITICAL:
        return "CRITICAL", "bold red"

    if rate > ERROR_RATE_WARNING:
        return "WARNING", "yellow"

    return "HEALTHY", "green"


def overall_status(statuses: list[str]) -> tuple[str, str]:
    """Determine overall workload health."""

    if "CRITICAL" in statuses:
        return "CRITICAL", "bold red"

    if "WARNING" in statuses:
        return "WARNING", "yellow"

    return "HEALTHY", "green"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():

    console.print("\n" * 4)

    console.print(
        Panel.fit(
            "[bold cyan]Enterprise AI Observability & Engineering Telemetry[/bold cyan]",
            border_style="cyan",
        )
    )

    prompts = load_prompts()

    if len(prompts) > MAX_REQUESTS:
        prompts = prompts[:MAX_REQUESTS]

    console.print()
    console.print("[green]✓ Workload loaded successfully[/green]")
    console.print(f"Model            : {MODEL_NAME}")
    console.print(f"Workload Size    : {len(prompts)} requests")

    # -----------------------------------------------------------------------
    # Request Execution
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]AI Request Execution[/bold]")

    records = []

    for index, prompt in enumerate(prompts, start=1):

        request_id = f"req-{index:03d}"

        console.print(f"\nRequest {index}/{len(prompts)}")
        console.print(f"Request ID       : {request_id}")

        try:

            result = invoke_model(
                model_name=MODEL_NAME,
                prompt=prompt,
            )

            latency = result["latency"]

            latency_status, latency_style = classify_latency(latency)

            record = {
                "request_id": request_id,
                "model": result["model"],
                "status": "SUCCESS",
                "latency": latency,
                "latency_status": latency_status,
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "total_tokens": result["total_tokens"],
                "cost": result["cost"],
                "error": "",
            }

            console.print(
                f"[{latency_style}]✓ Request completed successfully[/{latency_style}]"
            )

            console.print(
                f"Latency          : {latency:.2f} sec "
                f"[{latency_style}]({latency_status})[/{latency_style}]"
            )

        except Exception as ex:

            record = {
                "request_id": request_id,
                "model": MODEL_NAME,
                "status": "FAILED",
                "latency": 0.0,
                "latency_status": "CRITICAL",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "cost": 0.0,
                "error": str(ex),
            }

            console.print("[bold red]✗ Request failed[/bold red]")
            console.print(f"[red]Error            : {ex}[/red]")

        records.append(record)

    # -----------------------------------------------------------------------
    # Request Telemetry
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Request Telemetry[/bold]")

    table = Table(title="AI Request Telemetry")

    table.add_column("Request")
    table.add_column("Model")
    table.add_column("Status")
    table.add_column("Latency")
    table.add_column("Latency Health")
    table.add_column("Tokens")
    table.add_column("Cost ($)")

    for record in records:

        if record["status"] == "SUCCESS":

            status_text = "[green]✓ SUCCESS[/green]"
            latency_text = f"{record['latency']:.2f} sec"

            if record["latency_status"] == "CRITICAL":
                health_text = "[bold red]CRITICAL[/bold red]"

            elif record["latency_status"] == "WARNING":
                health_text = "[yellow]WARNING[/yellow]"

            else:
                health_text = "[green]HEALTHY[/green]"

        else:

            status_text = "[bold red]✗ FAILED[/bold red]"
            latency_text = "-"
            health_text = "[bold red]CRITICAL[/bold red]"

        table.add_row(
            record["request_id"],
            record["model"],
            status_text,
            latency_text,
            health_text,
            str(record["total_tokens"]),
            f"{record['cost']:.6f}",
        )

    console.print(table)

    # -----------------------------------------------------------------------
    # Aggregate Metrics
    # -----------------------------------------------------------------------

    total_requests = len(records)

    successful = sum(
        record["status"] == "SUCCESS"
        for record in records
    )

    failed = total_requests - successful

    successful_records = [
        record
        for record in records
        if record["status"] == "SUCCESS"
    ]

    latencies = [
        record["latency"]
        for record in successful_records
    ]

    average_latency = mean(latencies) if latencies else 0.0
    fastest_latency = min(latencies) if latencies else 0.0
    slowest_latency = max(latencies) if latencies else 0.0

    success_rate = (
        successful / total_requests * 100
        if total_requests
        else 0.0
    )

    error_rate = (
        failed / total_requests * 100
        if total_requests
        else 0.0
    )

    total_input_tokens = sum(
        record["input_tokens"]
        for record in records
    )

    total_output_tokens = sum(
        record["output_tokens"]
        for record in records
    )

    total_tokens = sum(
        record["total_tokens"]
        for record in records
    )

    total_cost = sum(
        record["cost"]
        for record in records
    )

    average_cost = (
        total_cost / successful
        if successful
        else 0.0
    )

    average_latency_status, average_latency_style = (
        classify_average_latency(average_latency)
    )

    success_status, success_style = (
        classify_success_rate(success_rate)
    )

    error_status, error_style = (
        classify_error_rate(error_rate)
    )

    workload_status, _ = overall_status(
        [
            average_latency_status,
            success_status,
            error_status,
        ]
    )

    # -----------------------------------------------------------------------
    # Engineering Metrics
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Engineering Metrics[/bold]")

    metrics = Table(title="AI Observability Summary")

    metrics.add_column("Metric")
    metrics.add_column("Value")
    metrics.add_column("Health")

    metrics.add_row(
        "Requests",
        str(total_requests),
        "-",
    )

    metrics.add_row(
        "Successful Requests",
        str(successful),
        f"[{success_style}]{success_status}[/{success_style}]",
    )

    metrics.add_row(
        "Failed Requests",
        str(failed),
        f"[{error_style}]{error_status}[/{error_style}]",
    )

    metrics.add_row(
        "Success Rate",
        f"{success_rate:.2f}%",
        f"[{success_style}]{success_status}[/{success_style}]",
    )

    metrics.add_row(
        "Error Rate",
        f"{error_rate:.2f}%",
        f"[{error_style}]{error_status}[/{error_style}]",
    )

    metrics.add_row(
        "Average Latency",
        f"{average_latency:.2f} sec",
        f"[{average_latency_style}]{average_latency_status}[/{average_latency_style}]",
    )

    metrics.add_row(
        "Fastest Request",
        f"{fastest_latency:.2f} sec",
        "-",
    )

    metrics.add_row(
        "Slowest Request",
        f"{slowest_latency:.2f} sec",
        "-",
    )

    console.print(metrics)

    # -----------------------------------------------------------------------
    # Token & Cost Telemetry
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Token & Cost Telemetry[/bold]")

    token_cost = Table(title="AI Consumption Metrics")

    token_cost.add_column("Metric")
    token_cost.add_column("Value")

    token_cost.add_row(
        "Input Tokens",
        f"{total_input_tokens:,}",
    )

    token_cost.add_row(
        "Output Tokens",
        f"{total_output_tokens:,}",
    )

    token_cost.add_row(
        "Total Tokens",
        f"{total_tokens:,}",
    )

    token_cost.add_row(
        "Total Cost",
        f"${total_cost:.6f}",
    )

    token_cost.add_row(
        "Average Cost / Request",
        f"${average_cost:.6f}",
    )

    console.print(token_cost)

    # -----------------------------------------------------------------------
    # Observability Thresholds
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Observability Thresholds[/bold]")

    thresholds = Table(title="Demonstration Thresholds")

    thresholds.add_column("Metric")
    thresholds.add_column("Healthy")
    thresholds.add_column("Warning")
    thresholds.add_column("Critical")

    thresholds.add_row(
        "Average Latency",
        f"< {AVG_LATENCY_WARNING:.0f} sec",
        f"{AVG_LATENCY_WARNING:.0f}–{AVG_LATENCY_CRITICAL:.0f} sec",
        f">= {AVG_LATENCY_CRITICAL:.0f} sec",
    )

    thresholds.add_row(
        "Request Latency",
        f"< {REQUEST_LATENCY_WARNING:.0f} sec",
        f"{REQUEST_LATENCY_WARNING:.0f}–{REQUEST_LATENCY_CRITICAL:.0f} sec",
        f">= {REQUEST_LATENCY_CRITICAL:.0f} sec",
    )

    thresholds.add_row(
        "Success Rate",
        f">= {SUCCESS_RATE_WARNING:.0f}%",
        f"{SUCCESS_RATE_CRITICAL:.0f}–{SUCCESS_RATE_WARNING:.1f}%",
        f"< {SUCCESS_RATE_CRITICAL:.0f}%",
    )

    thresholds.add_row(
        "Error Rate",
        f"<= {ERROR_RATE_WARNING:.0f}%",
        f"{ERROR_RATE_WARNING:.0f}–{ERROR_RATE_CRITICAL:.0f}%",
        f"> {ERROR_RATE_CRITICAL:.0f}%",
    )

    console.print(thresholds)

    # -----------------------------------------------------------------------
    # Observability Assessment
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Observability Assessment[/bold]")

    critical_breaches = []
    warning_breaches = []

    if average_latency_status == "CRITICAL":

        critical_breaches.append(
            f"• Average latency : {average_latency:.2f} sec "
            f"(threshold: >= {AVG_LATENCY_CRITICAL:.0f} sec)"
        )

    elif average_latency_status == "WARNING":

        warning_breaches.append(
            f"• Average latency : {average_latency:.2f} sec "
            f"(threshold: {AVG_LATENCY_WARNING:.0f}–"
            f"{AVG_LATENCY_CRITICAL:.0f} sec)"
        )

    for record in records:

        if record["status"] != "SUCCESS":

            critical_breaches.append(
                f"• {record['request_id']} : request failed"
            )

        elif record["latency_status"] == "CRITICAL":

            critical_breaches.append(
                f"• {record['request_id']} : "
                f"{record['latency']:.2f} sec "
                f"(threshold: >= "
                f"{REQUEST_LATENCY_CRITICAL:.0f} sec)"
            )

        elif record["latency_status"] == "WARNING":

            warning_breaches.append(
                f"• {record['request_id']} : "
                f"{record['latency']:.2f} sec "
                f"(threshold: "
                f"{REQUEST_LATENCY_WARNING:.0f}–"
                f"{REQUEST_LATENCY_CRITICAL:.0f} sec)"
            )

    reliability_status = (
        f"• Success Rate : {success_rate:.2f}%\n"
        f"• Error Rate   : {error_rate:.2f}%"
    )

    if workload_status == "HEALTHY":

        assessment = (
            "[bold green]● HEALTHY[/bold green]\n\n"
            "No configured observability threshold was breached.\n\n"
            "Reliability status:\n"
            f"{reliability_status}"
        )

        border = "green"

    elif workload_status == "WARNING":

        assessment = (
            "[yellow]● WARNING[/yellow]\n\n"
            "Warning conditions detected:\n\n"
            + "\n".join(warning_breaches)
            + "\n\nReliability status:\n"
            + reliability_status
        )

        border = "yellow"

    else:

        assessment = (
            "[bold red]● CRITICAL[/bold red]\n\n"
            "Critical conditions detected:\n\n"
            + "\n".join(critical_breaches)
            + "\n\nReliability status:\n"
            + reliability_status
        )

        if warning_breaches:

            assessment += (
                "\n\nAdditional warning conditions:\n\n"
                + "\n".join(warning_breaches)
            )

        border = "red"

    console.print(
        Panel.fit(
            assessment,
            border_style=border,
        )
    )

    # -----------------------------------------------------------------------
    # Engineering Recommendation
    # -----------------------------------------------------------------------

    console.print()
    console.rule("[bold]Engineering Recommendation[/bold]")

    recommendation = (
        "AI observability should capture request-level telemetry "
        "and aggregate it into actionable engineering signals.\n\n"
        "Latency, reliability, token consumption, and cost provide "
        "different perspectives of AI workload health.\n\n"
        "Thresholds should be treated as workload-specific "
        "demonstration values and replaced with SLO-driven "
        "baselines in production systems."
    )

    console.print(
        Panel.fit(
            recommendation,
            title="Key Engineering Insight",
            border_style="cyan",
        )
    )

    console.print("\n" * 4)


if __name__ == "__main__":
    main()