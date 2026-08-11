"""
===============================================================================
Enterprise AI Engineering Lab

Utility:
    Dynamic Model Routing

Objective:
    Demonstrate how an enterprise AI application can dynamically select an
    appropriate model for a request using an LLM-based routing decision.

    The utility compares fixed-model execution with dynamic model routing and
    measures the additional latency, token usage, and cost introduced by the
    routing decision.

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

PROMPT_FILE = Path("prompts/09_routing_demo.txt")

# Fixed model used as the baseline.
FIXED_MODEL = MODEL_NAME

# Candidate models available to the router.
# These can be changed centrally without changing the routing logic.
ROUTING_MODELS = [
    "gpt-5-nano",
    "gpt-5-mini",
]

ROUTER_MODEL = "gpt-5-nano"

# ---------------------------------------------------------------------------
# Model Pricing
# ---------------------------------------------------------------------------
#
# Pricing per 1 million tokens.
# Used to calculate the routing LLM cost separately from model execution cost.
# ---------------------------------------------------------------------------

MODEL_PRICING = {
    "gpt-5-nano": {
        "input": 0.05,
        "output": 0.40,
    },
    "gpt-5-mini": {
        "input": 0.25,
        "output": 2.00,
    },
}


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
# Cost Calculation
# ---------------------------------------------------------------------------

def calculate_token_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Calculate estimated token cost for a model.
    """

    pricing = MODEL_PRICING[model]

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output"]

    return input_cost + output_cost



# ---------------------------------------------------------------------------
# Routing Decision
# ---------------------------------------------------------------------------

def route_request(prompt: str) -> dict:
    """
    Use an LLM to determine the appropriate execution model.

    The router returns structured JSON containing:
        - complexity
        - reasoning
        - selected model
    """

    routing_prompt = f"""
You are an enterprise AI model router.

Analyze the following user request and select the most appropriate model
from the available models.

Available models:
{json.dumps(ROUTING_MODELS)}

Routing guidance:

- Use gpt-5-nano for simple factual questions, straightforward explanations,
  simple transformations, or tasks requiring limited reasoning.
- Use gpt-5-mini for requests requiring deeper reasoning, technical analysis,
  multi-step reasoning, architecture, or complex problem solving.

Return ONLY valid JSON using exactly this structure:

{{
  "complexity": "simple|complex",
  "reason": "brief explanation",
  "model": "selected model"
}}

User request:
{prompt}
"""

    start = time.perf_counter()

    response = client.responses.create(
        model=ROUTER_MODEL,
        input=routing_prompt,
    )

    latency = (
        time.perf_counter()
        - start
    )

    raw_output = response.output_text.strip()

    decision = json.loads(raw_output)

    decision["router_latency"] = latency

    decision["router_input_tokens"] = (
        response.usage.input_tokens
        if response.usage
        else 0
    )

    decision["router_output_tokens"] = (
        response.usage.output_tokens
        if response.usage
        else 0
    )

    decision["router_total_tokens"] = (
        response.usage.total_tokens
        if response.usage
        else 0
    )

    return decision


# ---------------------------------------------------------------------------
# Individual Fixed-Model Execution
# ---------------------------------------------------------------------------

def execute_fixed_model(
    prompts: list[str],
) -> dict:
    """
    Execute all prompts using the same fixed model.
    """

    console.print()
    console.rule(
        "[bold]Fixed Model Execution[/bold]"
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

        start = time.perf_counter()

        try:

            result = invoke_model(
                model_name=FIXED_MODEL,
                prompt=prompt,
            )

            latency = (
                time.perf_counter()
                - start
            )

            result["request"] = index
            result["status"] = "SUCCESS"
            result["latency"] = latency
            result["model"] = FIXED_MODEL

            results.append(result)

            console.print(
                "[green]✓ Request completed successfully[/green]"
            )

        except Exception as ex:

            latency = (
                time.perf_counter()
                - start
            )

            results.append(
                {
                    "request": index,
                    "status": "FAILED",
                    "latency": latency,
                    "model": FIXED_MODEL,
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

    return {
        "mode": "Fixed Model",
        "results": results,
        "requests": len(prompts),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "total_time": total_time,
        "input_tokens": sum(
            result["input_tokens"]
            for result in successful
        ),
        "output_tokens": sum(
            result["output_tokens"]
            for result in successful
        ),
        "total_tokens": sum(
            result["total_tokens"]
            for result in successful
        ),
        "cost": sum(
            result["cost"]
            for result in successful
        ),
    }


# ---------------------------------------------------------------------------
# Dynamic Routing Execution
# ---------------------------------------------------------------------------

def execute_dynamic_routing(
    prompts: list[str],
) -> dict:
    """
    Execute the same workload using LLM-based dynamic model routing.
    """

    console.print()
    console.rule(
        "[bold]Dynamic Model Routing[/bold]"
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

        try:

            # ---------------------------------------------------------------
            # Routing decision
            # ---------------------------------------------------------------

            routing_start = time.perf_counter()

            decision = route_request(
                prompt
            )

            routing_elapsed = (
                time.perf_counter()
                - routing_start
            )

            selected_model = decision["model"]

            console.print(
                f"Routing Decision : "
                f"{decision['complexity']}"
            )

            console.print(
                f"Selected Model   : "
                f"{selected_model}"
            )

            # ---------------------------------------------------------------
            # Execute request using selected model
            # ---------------------------------------------------------------

            execution_start = time.perf_counter()

            result = invoke_model(
                model_name=selected_model,
                prompt=prompt,
            )

            execution_latency = (
                time.perf_counter()
                - execution_start
            )

            result["request"] = index
            result["status"] = "SUCCESS"

            result["routing_complexity"] = (
                decision["complexity"]
            )

            result["routing_reason"] = (
                decision["reason"]
            )

            result["selected_model"] = (
                selected_model
            )

            result["router_latency"] = (
                decision["router_latency"]
            )

            result["routing_elapsed"] = (
                routing_elapsed
            )

            result["execution_latency"] = (
                execution_latency
            )

            result["router_input_tokens"] = (
                decision["router_input_tokens"]
            )

            result["router_output_tokens"] = (
                decision["router_output_tokens"]
            )

            result["router_total_tokens"] = (
                decision["router_total_tokens"]
            )

            results.append(result)

            console.print(
                "[green]✓ Request completed successfully[/green]"
            )

        except Exception as ex:

            results.append(
                {
                    "request": index,
                    "status": "FAILED",
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

    # -----------------------------------------------------------------------
    # Routing metrics
    # -----------------------------------------------------------------------

    router_input_tokens = sum(
        result["router_input_tokens"]
        for result in successful
    )

    router_output_tokens = sum(
        result["router_output_tokens"]
        for result in successful
    )

    router_total_tokens = sum(
        result["router_total_tokens"]
        for result in successful
    )

    # The router itself uses the router model. Calculate its cost using the
    # same common cost information returned by invoke_model where possible.
    #
    # We deliberately keep router cost separate from execution cost.
    router_cost = calculate_token_cost(
        model=ROUTER_MODEL,
        input_tokens=router_input_tokens,
        output_tokens=router_output_tokens,
    )

    execution_cost = sum(
        result["cost"]
        for result in successful
    )

    total_cost = (
        router_cost
        + execution_cost
    )

    return {
        "mode": "Dynamic Routing",
        "results": results,
        "requests": len(prompts),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "total_time": total_time,
        "router_input_tokens": router_input_tokens,
        "router_output_tokens": router_output_tokens,
        "router_total_tokens": router_total_tokens,
        "router_cost": router_cost,
        "execution_input_tokens": sum(
            result["input_tokens"]
            for result in successful
        ),
        "execution_output_tokens": sum(
            result["output_tokens"]
            for result in successful
        ),
        "execution_total_tokens": sum(
            result["total_tokens"]
            for result in successful
        ),
        "execution_cost": execution_cost,

        "router_cost": router_cost,
        "execution_input_tokens": sum(
            result["input_tokens"]
            for result in successful
        ),
        "execution_output_tokens": sum(
            result["output_tokens"]
            for result in successful
        ),
        "execution_total_tokens": sum(
            result["total_tokens"]
            for result in successful
        ),
        "execution_cost": execution_cost,
        "total_cost": total_cost,
    }

    

# ---------------------------------------------------------------------------
# Routing Metrics
# ---------------------------------------------------------------------------

def display_routing_metrics(
    dynamic: dict,
) -> None:
    """
    Display routing decisions and selected models.
    """

    console.print()

    console.rule(
        "[bold]Routing Decisions[/bold]"
    )

    table = Table(
        title="Dynamic Model Routing"
    )

    table.add_column(
        "Request",
        justify="center",
    )

    table.add_column(
        "Complexity",
    )

    table.add_column(
        "Selected Model",
    )

    table.add_column(
        "Router Latency",
        justify="right",
    )

    table.add_column(
        "Execution Latency",
        justify="right",
    )

    for result in dynamic["results"]:

        if result["status"] == "SUCCESS":

            table.add_row(
                str(result["request"]),
                result["routing_complexity"],
                result["selected_model"],
                f"{result['router_latency']:.2f} sec",
                f"{result['execution_latency']:.2f} sec",
            )

    console.print(table)


# ---------------------------------------------------------------------------
# Execution Comparison
# ---------------------------------------------------------------------------

def display_comparison(
    fixed: dict,
    dynamic: dict,
) -> None:
    """
    Compare fixed-model execution with dynamic routing.
    """

    console.print()

    console.rule(
        "[bold]Execution Comparison[/bold]"
    )

    table = Table(
        title="Fixed Model vs Dynamic Routing"
    )

    table.add_column("Metric")

    table.add_column(
        "Fixed Model",
        justify="right",
    )

    table.add_column(
        "Dynamic Routing",
        justify="right",
    )

    table.add_row(
        "Requests",
        str(fixed["requests"]),
        str(dynamic["requests"]),
    )

    table.add_row(
        "Successful",
        str(fixed["successful"]),
        str(dynamic["successful"]),
    )

    table.add_row(
        "Failed",
        str(fixed["failed"]),
        str(dynamic["failed"]),
    )

    table.add_row(
        "Execution Time",
        f"{fixed['total_time']:.2f} sec",
        f"{dynamic['total_time']:.2f} sec",
    )

    table.add_row(
        "Input Tokens",
        str(fixed["input_tokens"]),
        str(dynamic["execution_input_tokens"]),
    )

    table.add_row(
        "Output Tokens",
        str(fixed["output_tokens"]),
        str(dynamic["execution_output_tokens"]),
    )

    table.add_row(
        "Total Tokens",
        str(fixed["total_tokens"]),
        str(dynamic["execution_total_tokens"]),
    )

    table.add_row(
        "Model Execution Cost",
        f"${fixed['cost']:.6f}",
        f"${dynamic['execution_cost']:.6f}",
    )

    table.add_row(
        "Router Tokens",
        "-",
        str(dynamic["router_total_tokens"]),
    )

    table.add_row(
        "Router Cost",
        "-",
        f"${dynamic['router_cost']:.6f}",
    )

    table.add_row(
        "Total Cost",
        f"${fixed['cost']:.6f}",
        f"${dynamic['total_cost']:.6f}",
    )

    console.print(table)


# ---------------------------------------------------------------------------
# Engineering Recommendation
# ---------------------------------------------------------------------------

def display_recommendation() -> None:
    """
    Display the engineering recommendation.
    """

    console.print()

    console.rule(
        "[bold]Engineering Recommendation[/bold]"
    )

    recommendation = Panel.fit(
        "[bold]Key Engineering Insight[/bold]\n\n"
        "Dynamic model routing can match different requests with "
        "different model capabilities, but the routing layer itself "
        "introduces measurable latency, token consumption, and cost.\n\n"
        "Routing is most valuable for heterogeneous workloads where "
        "different requests have meaningfully different model "
        "requirements.\n\n"
        "For homogeneous workloads, a fixed model may provide simpler "
        "and more predictable execution.\n\n"
        "The value of routing should therefore be evaluated against "
        "the additional routing overhead.",
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
    Entry point for the dynamic model routing demonstration.
    """

    prompts = load_prompts()

    console.print("\n" * 4)

    console.print(
        Panel.fit(
            "[bold cyan]"
            "Enterprise Dynamic Model Routing"
            "[/bold cyan]",
            border_style="cyan",
        )
    )

    console.print()

    console.print(
        "[green]✓ Workload loaded successfully[/green]"
    )

    console.print(
        f"Fixed Model      : {FIXED_MODEL}"
    )

    console.print(
        f"Router Model     : {ROUTER_MODEL}"
    )

    console.print(
        f"Candidate Models : {', '.join(ROUTING_MODELS)}"
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
    # Execute both strategies using the same workload.
    # -----------------------------------------------------------------------

    fixed = execute_fixed_model(
        prompts
    )

    dynamic = execute_dynamic_routing(
        prompts
    )

    # -----------------------------------------------------------------------
    # Display routing decisions and comparison.
    # -----------------------------------------------------------------------

    display_routing_metrics(
        dynamic
    )

    display_comparison(
        fixed,
        dynamic,
    )

    display_recommendation()

    console.print("\n" * 4)


# ---------------------------------------------------------------------------
# Program Entry
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()