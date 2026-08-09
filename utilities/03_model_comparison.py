"""
===============================================================================
Enterprise AI Engineering Lab

Release 3 : Model Comparison

Engineering Question

Given the same prompt,
how do different LLM models compare in terms of:

- Latency
- Token Usage
- Estimated Cost

===============================================================================
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from common.llm import compare_models

console = Console()

def read_prompt() -> str:
    """
    Read sample prompt.
    """
    
    return Path("prompts/sample_prompt.txt").read_text(
        encoding="utf-8"
    )


def build_table(results):

    table = Table(
        title="Enterprise AI Model Comparison"
    )

    table.add_column("Model", style="cyan")
    table.add_column("Latency (sec)", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost ($)", justify="right")

    for result in results:
        table.add_row(
            result["model"],
            f"{result['latency']:.2f}",
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"{result['cost']:.6f}"
        )

    return table


def print_summary(results):

    fastest = min(
        results,
        key=lambda x: x["latency"]
    )

    cheapest = min(
        results,
        key=lambda x: x["cost"]
    )

    lowest_tokens = min(
        results,
        key=lambda x: x["total_tokens"]
    )

    console.print()

    console.rule("[bold blue]Engineering Summary")

    console.print(
        f" ⚡ Fastest Model       : {fastest['model']}"
    )

    console.print(
        f" 💰 Lowest Cost        : {cheapest['model']}"
    )

    console.print(
        f"📦 Lowest Token Usage : {lowest_tokens['model']}"
    )

def main():
    prompt = read_prompt()
    results = compare_models(prompt)
    console.print()
    console.print(
        build_table(results)
    )
    print_summary(results)

if __name__ == "__main__":
    main()