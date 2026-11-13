"""Illustrative monthly inference budget from staking rewards and token usage."""
import math
from decimal import Decimal

from .common import metric

OVERVIEW = "https://docs.near.ai/cloud/staking-for-inference/overview"
CALCULATOR = "https://docs.near.ai/cloud/staking-for-inference/calculator"
PRICING = "https://near.ai/pricing"

DEFAULTS = {
    "staked_near": 1000,
    "near_price_usd": 2,
    "net_apy_pct": 6,
    "input_million": 25,
    "output_million": 10,
    "input_usd_per_million": 0.2,
    "output_usd_per_million": 1,
}
BOUNDS = {
    "staked_near": (0, 1e9),
    "near_price_usd": (0.000001, 1e6),
    "net_apy_pct": (0, 100),
    "input_million": (0, 1e6),
    "output_million": (0, 1e6),
    "input_usd_per_million": (0, 1e6),
    "output_usd_per_million": (0, 1e6),
}


def collect(parameters=None):
    if parameters is not None and not isinstance(parameters, dict):
        raise ValueError("Scenario parameters must be an object")
    values = {**DEFAULTS, **(parameters or {})}
    if set(values) != set(DEFAULTS):
        raise ValueError("Unknown inference parameter")
    for name, value in values.items():
        low, high = BOUNDS[name]
        if (type(value) not in (int, float) or not low <= value <= high
                or not math.isfinite(value)):
            raise ValueError(f"{name} must be a number between {low} and {high}")
    if 0 < values["net_apy_pct"] < 0.01:
        raise ValueError("Enter zero or at least 0.01% for the net annual reward")
    return {"assumptions": values}


def analyze(evidence):
    assumptions = collect(evidence["assumptions"])["assumptions"]
    p = {name: Decimal(str(value)) for name, value in assumptions.items()}
    input_cost = p["input_million"] * p["input_usd_per_million"]
    output_cost = p["output_million"] * p["output_usd_per_million"]
    bill = input_cost + output_cost
    # Flat annual reward assumption, expressed as an average monthly credit rate.
    per_near = p["near_price_usd"] * p["net_apy_pct"] / 1200
    credit = p["staked_near"] * per_near
    shortfall = max(Decimal(0), bill - credit)
    required = bill / per_near if per_near else (Decimal(0) if not bill else None)

    rows = []
    for label, factor in (("Half the assumed NEAR price", Decimal("0.5")),
                          ("Your assumptions", Decimal(1)),
                          ("1.5× the assumed NEAR price", Decimal("1.5"))):
        monthly = credit * factor
        rows.append({
            "Price scenario": label,
            "NEAR price (USD)": float(p["near_price_usd"] * factor),
            "Monthly credit (USD of usage)": float(monthly),
            "Uncovered bill (USD)": float(max(Decimal(0), bill - monthly)),
            "Stake needed (NEAR)": "Unavailable" if required is None else float(required / factor),
        })

    return {
        "headline": "Estimate how much inference your stake could cover.",
        "summary": f"The assumed monthly workload costs ${bill:,.4f} (${input_cost:,.4f} input and "
                   f"${output_cost:,.4f} output). The stake would generate ${credit:,.4f} of monthly usage credit.",
        "metrics": [metric("Monthly inference bill", float(bill), "USD"),
                    metric("Estimated monthly credit", float(credit), "USD of usage"),
                    metric("Uncovered bill", float(shortfall), "USD"),
                    metric("Stake to cover the bill", "Unavailable" if required is None else float(required), "NEAR")],
        "rows": rows,
        "supports": "The model connects staked NEAR to a metered AI workload. The price scenarios hold the reward rate and usage constant.",
        "investment_link": "Inference can give NEAR a role in funding a recurring service through staking rewards. Actual uptake determines the size of that use.",
        "limits": "This planning scenario uses an average month and an assumed net annual reward rate after validator commission. "
                  "It keeps price, stake, and token usage constant within each row and omits compounding and existing credit balances. "
                  "Live rates, eligible services and credits depend on the product. This is the inference model.",
    }
