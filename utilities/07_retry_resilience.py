"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    Retry & Resilience

Objective:
    Demonstrate how enterprise AI applications automatically recover
    from transient failures using configurable retry strategies.

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

PROMPT_FILE = Path("prompts/07_retry_demo.txt")

MAX_RETRIES = 3

INITIAL_RETRY_DELAY = 1

TRANSIENT_EXCEPTIONS = (
    TimeoutError,
    RuntimeError,
)

# ---------------------------------------------------------------------------
# Prompt Loader
# ---------------------------------------------------------------------------

def load_prompt() -> str:
    """
    Load the prompt used for demonstrating retry behaviour.
    """

    return PROMPT_FILE.read_text(
        encoding="utf-8"
    ).strip()


# ---------------------------------------------------------------------------
# Failure Simulator
#
# Simulates transient failures before allowing the LLM invocation to succeed.
# This ensures deterministic behaviour for every execution.
# ---------------------------------------------------------------------------

SIMULATED_FAILURES = [

    TimeoutError(
        "Connection timeout."
    ),

    RuntimeError(
        "HTTP 429 - Rate limit exceeded."
    ),

    None
]


class FailureSimulator:
    """
    Simulates transient failures before allowing
    the request to succeed.
    """

    def __init__(self):

        self.attempt = 0

    def invoke(
        self,
        prompt: str
    ) -> dict:

        failure = SIMULATED_FAILURES[
            self.attempt
        ]

        self.attempt += 1

        if failure:
            raise failure

        return invoke_model(
            model_name=MODEL_NAME,
            prompt=prompt
        )


# ---------------------------------------------------------------------------
# Retry Demonstration
# ---------------------------------------------------------------------------

def execute_with_retry(
    prompt: str,
) -> tuple[list[dict], dict | None]:

    """
    Execute the prompt using retry logic.

    Returns
    -------
    tuple

        (
            retry_history,
            successful_result
        )
    """

    simulator = FailureSimulator()

    retry_history = []

    retry_delay = INITIAL_RETRY_DELAY

    attempt = 1

    result = None

    while attempt <= MAX_RETRIES:

        console.print(f"\nAttempt {attempt}...")

        try:

            result = simulator.invoke(prompt)

            retry_history.append(
                {
                    "attempt": attempt,
                    "status": "SUCCESS",
                    "details": "Request completed successfully",
                }
            )

            console.print(
                "[green]✓ Request completed successfully[/green]"
            )

            break

        except TRANSIENT_EXCEPTIONS as ex:

            retry_history.append(
                {
                    "attempt": attempt,
                    "status": "FAIL",
                    "details": str(ex),
                }
            )

            console.print(
                f"[red]✗ {ex}[/red]"
            )

            if attempt == MAX_RETRIES:

                console.print(
                    "\n[red]Maximum retry attempts exceeded.[/red]"
                )

                break

            unit = "second" if retry_delay == 1 else "seconds"

            console.print(
                f"[yellow]Retrying in {retry_delay} {unit}...[/yellow]"
            )

            #
            # Simulate exponential backoff.
            # Keep the delay short so the utility
            # remains quick to execute.
            #
            time.sleep(min(retry_delay, 2))

            retry_delay *= 2

            attempt += 1

    return (
        retry_history,
        result
    )


# ---------------------------------------------------------------------------
# Retry Metrics
# ---------------------------------------------------------------------------

def display_engineering_metrics(
    retry_history: list[dict],
) -> None:
    """
    Display retry history.
    """

    console.print()

    console.rule(
        "[bold]Engineering Metrics[/bold]"
    )

    table = Table(
        title="Retry Attempt Summary"
    )

    table.add_column(
        "Attempt",
        justify="center"
    )

    table.add_column(
        "Status",
        justify="center"
    )

    table.add_column(
        "Details"
    )

    for item in retry_history:

        table.add_row(
            str(item["attempt"]),
            item["status"],
            item["details"],
        )

    console.print(table)


# ---------------------------------------------------------------------------
# Engineering Summary
# ---------------------------------------------------------------------------

def display_engineering_summary(
    retry_history: list[dict],
    result: dict | None,
) -> None:
    """
    Display engineering summary.
    """

    console.print()

    console.rule(
        "[bold]Engineering Summary[/bold]"
    )

    retries = max(
        len(retry_history) - 1,
        0
    )

    final_status = (
        "SUCCESS"
        if result
        else "FAILED"
    )

    console.print(
        f"Attempts           : {len(retry_history)}"
    )

    console.print(
        f"Retries            : {retries}"
    )

    console.print(
        f"Final Status       : {final_status}"
    )

    if result:

        console.print(
            f"Latency            : {result['latency']:.2f} sec"
        )

        console.print(
            f"Input Tokens       : {result['input_tokens']}"
        )

        console.print(
            f"Output Tokens      : {result['output_tokens']}"
        )

        console.print(
            f"Total Tokens       : {result['total_tokens']}"
        )

        console.print(
            f"Estimated Cost     : ${result['cost']:.6f}"
        )

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Entry point for the retry and resilience demonstration.
    """

    prompt = load_prompt()

    console.print("\n" * 4)

    console.print(
        Panel.fit(
            "[bold cyan]Enterprise Retry & Resilience[/bold cyan]",
            border_style="cyan",
        )
    )

    console.print()
    console.print("[green]✓ Prompt loaded successfully[/green]")
    console.print(f"Model            : {MODEL_NAME}")
    console.print(f"Prompt Length    : {len(prompt)} characters")

    console.print()
    console.rule("[bold]Retry Demonstration[/bold]")

    retry_history, result = execute_with_retry(prompt)

    display_engineering_metrics(retry_history)

    display_engineering_summary(
        retry_history,
        result
    )

    console.print()

    console.rule(
        "[bold]Engineering Recommendation[/bold]"
    )

    recommendation = Panel.fit(
        "[bold]Key Engineering Insight[/bold]\n\n"
        "Enterprise AI applications should retry only transient failures.\n"
        "Use exponential backoff to reduce downstream load and\n"
        "avoid aggressive retry storms.\n\n"
        "Retries improve application resilience, but retry limits\n"
        "and graceful failure handling are equally important.",
        border_style="cyan",
    )

    console.print(recommendation)

    console.print("\n" * 4)


# ---------------------------------------------------------------------------
# Program Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()