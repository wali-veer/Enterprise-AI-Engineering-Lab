"""
===============================================================================
Enterprise AI Engineering Lab

Module:
    Shared LLM Utilities

Objective:
    Provide reusable functions for invoking Large Language Models and
    collecting engineering metrics.

Author:
    Veeresh Wali

Repository:
    https://github.com/wali-veer/Enterprise-AI-Engineering-Lab
===============================================================================
"""

# imports
from __future__ import annotations

from typing import Dict, List

from time import perf_counter
from pydantic import BaseModel
from common.openai_client import client
from common.pricing import estimate_cost


# ---------------------------------------------------------------------------
# APIs
# ---------------------------------------------------------------------------
#
# invoke_model()
# invoke_model_with_limit()
# invoke_structured_model()
#
# ---------------------------------------------------------------------------

SUPPORTED_MODELS: List[str] = [
    "gpt-5.4",
    "gpt-5.4-nano",
    "gpt-5.4-mini",
]


def invoke_model(model_name: str, prompt: str) -> Dict:
    """
    Invoke an LLM and return engineering metrics.

    Parameters
    ----------
    model_name
        Name of the model.

    prompt
        User prompt.

    Returns
    -------
    dict

    Example
    {
        "model": "gpt-5",
        "latency": 1.42,
        "input_tokens": 45,
        "output_tokens": 188,
        "total_tokens": 233,
        "cost": 0.00452,
        "response": "..."
    }
    """

    start = perf_counter()

    response = client.responses.create(
        model=model_name,
        input=prompt
    )

    latency = perf_counter() - start

    usage = response.usage

    cost = estimate_cost(
        model=model_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens
    )

    return {
        "model": model_name,
        "latency": latency,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
        "cost": cost["total_cost"],
        "response": response.output_text
    }


def compare_models(prompt: str) -> List[Dict]:
    """
    Execute the same prompt against every supported model.

    Parameters
    ----------
    prompt
        Prompt to execute.

    Returns
    -------
    list[dict]
        Engineering metrics for every model.
    """

    results = []

    for model in SUPPORTED_MODELS:
        results.append(
            invoke_model(
                model_name=model,
                prompt=prompt
            )
        )

    return results

# ---------------------------------------------------------------------------
# Response Control Utility
# Executes a prompt while limiting the maximum number of output tokens.
# ---------------------------------------------------------------------------

def invoke_model_with_limit(
    model_name: str,
    prompt: str,
    max_output_tokens: int
) -> Dict:
    """
    Execute a prompt using a maximum output token limit.

    Parameters
    ----------
    model_name
        LLM model name.

    prompt
        Prompt to execute.

    max_output_tokens
        Maximum response length.

    Returns
    -------
    dict
        Engineering metrics.
    """

    start = perf_counter()

    response = client.responses.create(
        model=model_name,
        input=prompt,
        max_output_tokens=max_output_tokens
    )

    latency = perf_counter() - start

    usage = response.usage

    cost = estimate_cost(
        model=model_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens
    )

    return {
        "limit": max_output_tokens,
        "latency": latency,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
        "cost": cost["total_cost"],
        "response": response.output_text
    }

# ---------------------------------------------------------------------------
# Structured Output
# ---------------------------------------------------------------------------
def invoke_structured_model(
    model_name: str,
    prompt: str,
    response_schema: type[BaseModel],
    instructions: str | None = None,
) -> Dict:
    """
    Invoke an OpenAI model and parse the response into
    a Pydantic model.

    Parameters
    ----------
    model_name
        Name of the OpenAI model.

    prompt
        Prompt to send to the model.

    response_schema
        Pydantic model describing the expected response.

    Returns
    -------
    dict
        Standardized engineering metrics together with
        the parsed structured response.
    """

    start_time = perf_counter()

    request = {
        "model": model_name,
        "input": prompt,
        "text_format": response_schema,
    }

    if instructions:
        request["instructions"] = instructions

    response = client.responses.parse(**request)

    latency = perf_counter() - start_time

    usage = response.usage

    cost = estimate_cost(
        model=model_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens
    )

    return {
        "model": model_name,
        "latency": latency,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
        "cost": cost["total_cost"],
        "structured_response": response.output_parsed,
        "schema_valid": response.output_parsed is not None,
    }