"""
===============================================================================

Enterprise AI Engineering Lab

Release 4 : Response Controls

Engineering Question

How does max_output_tokens influence latency,
token usage and estimated cost?

===============================================================================
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from common.config import MODEL_NAME
from common.llm import invoke_model_with_limit

console = Console()

OUTPUT_LIMITS = [
    50,
    100,
    250,
    500
]


def read_prompt() -> str:
    return Path(
        "prompts/sample_prompt.txt"
    ).read_text(
        encoding="utf-8"
    )

def main():

    prompt = read_prompt()

    table = Table(
        title="LLM Response Control Comparison"
    )

    table.add_column("Max Output", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost ($)", justify="right")

    results = []

    for limit in OUTPUT_LIMITS:

        result = invoke_model_with_limit(
            MODEL_NAME,
            prompt,
            limit
        )

        results.append(result)

        table.add_row(
            str(limit),
            f"{result['latency']:.2f}",
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"{result['cost']:.6f}"
        )

    console.print()
    console.print(table)

    console.rule("[bold blue]Engineering Observations")

    lowest_cost = min(
        results,
        key=lambda x: x["cost"]
    )

    fastest = min(
        results,
        key=lambda x: x["latency"]
    )

    console.print(
        f"⚡ Fastest Configuration : {fastest['limit']} output tokens"
    )

    console.print(
        f"💰 Lowest Cost           : {lowest_cost['limit']} output tokens"
    )

    console.print()

    console.print(
        "[bold green]Recommendation[/bold green]"
    )

    console.print(
        "Configure max_output_tokens according to business "
        "requirements instead of allowing unnecessarily "
        "long responses."
    )

if __name__ == "__main__":
    main()