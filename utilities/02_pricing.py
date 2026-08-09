"""
Enterprise AI Engineering Lab

Release 2 : Pricing

Goal

Calculate the estimated cost of an OpenAI request
using the actual token usage returned by the API.
"""

from pathlib import Path
import time

from rich.console import Console
from rich.table import Table

from common.config import MODEL_NAME
from common.openai_client import client

from common.pricing import estimate_cost

console = Console()

def read_prompt():
    return Path("prompts/sample_prompt.txt").read_text(
        encoding="utf-8"
    )

prompt = read_prompt()

start = time.perf_counter()

response = client.responses.create(
    model=MODEL_NAME,
    input=prompt
)

elapsed = time.perf_counter() - start

usage = response.usage

cost = estimate_cost(
    MODEL_NAME,
    usage.input_tokens,
    usage.output_tokens
)

table = Table(title=" Pricing Analysis")

table.add_column("Metric")
table.add_column("Value")

table.add_row("Model", MODEL_NAME)

table.add_row("Latency", f"{elapsed:.2f} sec")

table.add_row("Input Tokens", str(usage.input_tokens))

table.add_row("Output Tokens", str(usage.output_tokens))

table.add_row("Total Tokens", str(usage.total_tokens))

table.add_row(
    "Input Cost",
    f"${cost['input_cost']:.8f}"
)

table.add_row(
    "Output Cost",
    f"${cost['output_cost']:.8f}"
)

table.add_row(
    "Total Cost",
    f"${cost['total_cost']:.8f}"
)

console.print(table)

console.rule("LLM Response")

console.print(response.output_text)