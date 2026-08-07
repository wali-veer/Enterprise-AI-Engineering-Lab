"""
===============================================================================
Enterprise AI Engineering Lab

Study:
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

from __future__ import annotations

import time
from typing import Dict, List

from openai import OpenAI

from common.openai_client import client
from common.pricing import estimate_cost


# ---------------------------------------------------------------------------
# Supported Models
#
# New models can be added here without modifying the engineering studies.
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

    start = time.perf_counter()

    response = client.responses.create(
        model=model_name,
        input=prompt
    )

    latency = time.perf_counter() - start

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