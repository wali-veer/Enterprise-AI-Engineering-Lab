"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    06 - Structured Output

Objective:
    Demonstrate why enterprise AI applications require structured responses
    instead of free-form natural language.

Author:
    Veeresh Wali

Repository:
    https://github.com/wali-veer/Enterprise-AI-Engineering-Lab
===============================================================================
"""

from pathlib import Path

from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel

from common.config import MODEL_NAME
from common.llm import invoke_model, invoke_structured_model


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#MODEL_NAME = DEFAULT_MODEL

PROMPT_FILE = (
    Path(__file__).resolve().parents[1]
    / "prompts"
    / "06_country_information.txt"
)

console = Console()


# ---------------------------------------------------------------------------
# Structured Response Schema
# ---------------------------------------------------------------------------

class CountryInformation(BaseModel):
    """
    Structured country information returned by the LLM.
    """

    country: str
    capital: str
    population: str
    currency: str


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def load_prompt() -> str:
    """
    Load the incident analysis prompt.

    Returns
    -------
    str
        Prompt loaded from the prompts directory.
    """

    return PROMPT_FILE.read_text(encoding="utf-8").strip()

# ---------------------------------------------------------------------------
# Demonstration Functions
# ---------------------------------------------------------------------------

def run_natural_language_demo(
    prompt: str,
    runs: int = 3
) -> list[dict]:
    """
    Execute the prompt multiple times using natural language responses.

    Parameters
    ----------
    prompt
        Prompt to execute.

    runs
        Number of executions.

    Returns
    -------
    list[dict]
        Engineering metrics for every execution.
    """

    results = []

    for _ in range(runs):
        results.append(
            invoke_model(
                model_name=MODEL_NAME,
                prompt=prompt
            )
        )

    return results


def run_structured_demo(
    prompt: str,
    runs: int = 3
) -> list[dict]:
    """
    Execute the prompt multiple times using structured output.

    Parameters
    ----------
    prompt
        Prompt to execute.

    runs
        Number of executions.

    Returns
    -------
    list[dict]
        Engineering metrics together with structured responses.
    """

    results = []

    for _ in range(runs):
        results.append(
            invoke_structured_model(
                model_name=MODEL_NAME,
                prompt=prompt,
                response_schema=CountryInformation
            )
        )

    return results

from rich.table import Table


# ---------------------------------------------------------------------------
# Display Functions
# ---------------------------------------------------------------------------

def display_natural_language_results(results: list[dict]) -> None:
    """
    Display engineering metrics and natural language responses.
    """

    console.print("\n")
    console.rule("[bold cyan]Natural Language Responses[/bold cyan]")

    table = Table(title="Engineering Metrics")

    table.add_column("Run", justify="center")
    table.add_column("Latency (sec)", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost ($)", justify="right")

    for index, result in enumerate(results, start=1):
        table.add_row(
            str(index),
            f"{result['latency']:.2f}",
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"{result['cost']:.6f}",
        )

    console.print(table)

    for index, result in enumerate(results, start=1):
        console.print(
            Panel(
                result["response"],
                title=f"Natural Language Response - Run {index}",
                expand=False,
            )
        )


def display_structured_results(results: list[dict]) -> None:
    """
    Display engineering metrics and structured responses.
    """

    console.print("\n")
    console.rule("[bold green]Structured Responses[/bold green]")

    metrics = Table(title="Engineering Metrics")

    metrics.add_column("Run", justify="center")
    metrics.add_column("Schema", justify="center")
    metrics.add_column("Latency (sec)", justify="right")
    metrics.add_column("Input", justify="right")
    metrics.add_column("Output", justify="right")
    metrics.add_column("Total", justify="right")
    metrics.add_column("Cost ($)", justify="right")

    for index, result in enumerate(results, start=1):

        schema = "PASS" if result["schema_valid"] else "FAIL"

        metrics.add_row(
            str(index),
            schema,
            f"{result['latency']:.2f}",
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"{result['cost']:.6f}",
        )

    console.print(metrics)

    for index, result in enumerate(results, start=1):

        report = result["structured_response"]

        table = Table(title=f"Structured Response - Run {index}")

        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Country", report.country)
        table.add_row("Capital", report.capital)
        table.add_row("Population", report.population)
        table.add_row("Currency", report.currency)

        console.print(table)


def display_engineering_summary(
    natural_results: list[dict],
    structured_results: list[dict],
) -> None:
    """
    Display engineering observations.
    """

    console.print()
    console.rule("[bold yellow]Engineering Validation[/bold yellow]")

    schema_valid = all(
        result["schema_valid"]
        for result in structured_results
    )

    console.print(
        "✓ Natural language responses may vary in wording and formatting "
        "between executions."
    )

    if schema_valid:
        console.print(
            "✓ Structured responses maintained a consistent schema "
            "across all executions."
        )
    else:
        console.print(
            "✗ One or more structured responses did not conform "
            "to the expected schema."
        )

    console.print(
        "✓ Structured responses maintain a consistent schema, making them easy to validate, parse, and integrate "
        "into downstream applications."
    )

    console.print()

    console.print(
        Panel(
            "[bold]Key Engineering Insight[/bold]\n\n"
            "Enterprise AI systems do not require deterministic text.\n\n"
            "They require deterministic structure.",
            title="Engineering Recommendation",
            expand=False,
        )
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    console.print(
        Panel.fit(
            "[bold cyan]Enterprise Structured Output Demonstration[/bold cyan]"
        )
    )

    prompt = load_prompt()

    natural_results = run_natural_language_demo(prompt)

    structured_results = run_structured_demo(prompt)

    display_natural_language_results(natural_results)

    display_structured_results(structured_results)

    display_engineering_summary(
        natural_results,
        structured_results,
    )


if __name__ == "__main__":
    main()