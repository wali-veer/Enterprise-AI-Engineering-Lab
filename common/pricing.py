"""
Enterprise AI Engineering Lab

Pricing Utility

Calculates the estimated cost of an OpenAI API request.

NOTE:
Update the pricing whenever OpenAI changes their published pricing.
"""

# Prices are in USD per 1 million tokens.
# Replace these values with the latest pricing from:
# https://platform.openai.com/docs/pricing

MODEL_PRICING = {
    "gpt-5": {
        "input": 1.25,
        "output": 10.00
    },
    "gpt-5-mini": {
        "input": 0.25,
        "output": 2.00
    },
    "gpt-5-nano": {
        "input": 0.05,
        "output": 0.40
    }
}


def estimate_cost(model: str,
                  input_tokens: int,
                  output_tokens: int):

    if model not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model}")

    pricing = MODEL_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost
    }