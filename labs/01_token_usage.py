"""
Enterprise AI Engineering Lab

Lab 01
Token Engineering

Sprint-1 Deliverable

Reads a prompt from a file,
invokes an OpenAI model,
prints the response,
prints token usage,
prints latency.
"""

from pathlib import Path
import time

from rich.console import Console
from rich.table import Table

from common.config import MODEL_NAME
from common.openai_client import client

console = Console()


def read_prompt() -> str:
    """
    Reads the sample prompt from the prompts folder.
    """
    prompt_file = Path("prompts/sample_prompt.txt")
    return prompt_file.read_text(encoding="utf-8")


def main():

    prompt = read_prompt()

    start = time.perf_counter()

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt
    )

    elapsed = time.perf_counter() - start

    usage = response.usage

    print("\n\n")
    
    table = Table(title="[bold blue] Enterprise AI Token Analyzer")

    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Model", MODEL_NAME)
    table.add_row("Latency", f"{elapsed:.2f} sec")
    table.add_row("Input Tokens", str(usage.input_tokens))
    table.add_row("Output Tokens", str(usage.output_tokens))
    table.add_row("Total Tokens", str(usage.total_tokens))

    console.print(table)

    console.rule("[bold blue]LLM Response")

    console.print(response.output_text)

    print("\n\n")


if __name__ == "__main__":
    main()