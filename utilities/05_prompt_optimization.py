"""
===============================================================================

Enterprise AI Engineering Lab

Utility 05

Prompt Optimization

Engineering Question

Can better prompt design reduce token usage,
latency, and operational cost while preserving
response quality?

===============================================================================
"""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from common.config import MODEL_NAME
from common.llm import invoke_model

console = Console()

PROMPTS = {
    "Verbose": "prompts/05_verbose_prompt.txt",
    "Optimized": "prompts/05_optimized_prompt.txt",
}


def read_prompt(file_path: str) -> str:
    """
    Read a prompt from disk.
    """
    return Path(file_path).read_text(encoding="utf-8")


def main():

    table = Table(title="Enterprise Prompt Optimization")

    table.add_column("Prompt")
    table.add_column("Latency (sec)", justify="right")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Total", justify="right")
    table.add_column("Cost ($)", justify="right")

    results = []

    for prompt_type, file_path in PROMPTS.items():

        prompt = read_prompt(file_path)

        result = invoke_model(
            MODEL_NAME,
            prompt
        )

        results.append(
            {
                "prompt": prompt_type,
                **result
            }
        )

        table.add_row(
            prompt_type,
            f"{result['latency']:.2f}",
            str(result["input_tokens"]),
            str(result["output_tokens"]),
            str(result["total_tokens"]),
            f"{result['cost']:.6f}",
        )

    console.print()
    console.print(table)

    console.rule("[bold blue]Engineering Summary")

    fastest = min(
        results,
        key=lambda x: x["latency"]
    )

    cheapest = min(
        results,
        key=lambda x: x["cost"]
    )

    smallest = min(
        results,
        key=lambda x: x["total_tokens"]
    )

    console.print(
        f"⚡ Fastest Prompt      : {fastest['prompt']}"
    )

    console.print(
        f"💰 Lowest Cost        : {cheapest['prompt']}"
    )

    console.print(
        f"📦 Lowest Token Usage : {smallest['prompt']}"
    )

    console.print()

    console.rule("[bold blue]Optimization Impact")

    verbose = next(
        result for result in results
        if result["prompt"] == "Verbose"
    )

    optimized = next(
        result for result in results
        if result["prompt"] == "Optimized"
    )

    console.print(
        f"📥 Input Tokens      : {calculate_improvement(verbose['input_tokens'], optimized['input_tokens']):.2f}% lower"
    )

    console.print(
        f"📤 Output Tokens     : {calculate_improvement(verbose['output_tokens'], optimized['output_tokens']):.2f}% lower"
    )

    console.print(
        f"📦 Total Tokens      : {calculate_improvement(verbose['total_tokens'], optimized['total_tokens']):.2f}% lower"
    )

    console.print(
        f"⚡ Latency           : {calculate_improvement(verbose['latency'], optimized['latency']):.2f}% faster"
    )

    console.print(
        f"💰 Estimated Cost    : {calculate_improvement(verbose['cost'], optimized['cost']):.2f}% lower"
    )

    console.print()

    console.print(
        "[bold green]Engineering Recommendation[/bold green]"
    )

    console.print(
        "Optimize prompts according to business objectives "
        "rather than simply reducing prompt length. "
        "Well-designed prompts can reduce operational "
        "cost while maintaining response quality."
    )

def calculate_improvement(baseline: float, optimized: float) -> float:
    """
    Calculate percentage improvement between two values.

    Parameters
    ----------
    baseline
        Original metric value.

    optimized
        Improved metric value.

    Returns
    -------
    float
        Percentage improvement.
    """

    if baseline == 0:
        return 0.0

    return ((baseline - optimized) / baseline) * 100



if __name__ == "__main__":
    main()