"""Illustrative annual model. These inputs are assumptions, not observed NEAR figures."""
import math
from .common import metric

DEFAULTS = {"annual_volume_usd": 1_000_000_000, "net_revenue_bps": 5,
            "allocation": 0.5, "near_price_usd": 2, "annual_issuance_near": 30_000_000,
            "burn_share": 0}
BOUNDS = {"annual_volume_usd": (0, 1e15), "net_revenue_bps": (0, 10000),
          "allocation": (0, 1), "near_price_usd": (0.000001, 1e6),
          "annual_issuance_near": (0, 1e12), "burn_share": (0, 1)}


def collect(parameters=None):
    values = dict(DEFAULTS)
    parameters = parameters or {}
    if set(parameters) - set(DEFAULTS):
        raise ValueError("Unknown scenario parameter")
    for name, value in parameters.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number")
        values[name] = value
    for name, value in values.items():
        low, high = BOUNDS[name]
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"{name} is outside its allowed range")
    return {"assumptions": values}


def analyze(evidence):
    p = collect(evidence["assumptions"])["assumptions"]
    revenue = p["annual_volume_usd"] * p["net_revenue_bps"] / 10000
    allocated = revenue * p["allocation"]
    bought = allocated / p["near_price_usd"]
    burned = bought * p["burn_share"]
    delta = p["annual_issuance_near"] - burned
    burn_per_dollar = p["net_revenue_bps"] / 10000 * p["allocation"] / p["near_price_usd"] * p["burn_share"]
    threshold = p["annual_issuance_near"] / burn_per_dollar if burn_per_dollar > 0 else None
    return {
        "headline": "Make the usage-to-token assumptions explicit.",
        "summary": "This model separates retained revenue, token purchases and permanent burns. "
                   "Every input is illustrative and editable; no current NEAR revenue or issuance is asserted.",
        "metrics": [metric("Annual retained revenue", round(revenue, 2), "USD"),
                    metric("Tokens purchased", round(bought, 4), "NEAR"),
                    metric("Tokens burned", round(burned, 4), "NEAR"),
                    metric("Net modeled supply change", round(delta, 4), "NEAR")],
        "rows": [{"Stage": "Retained revenue", "USD": round(revenue, 2)},
                 {"Stage": "Allocated to purchases", "USD": round(allocated, 2)},
                 {"Stage": "Purchased tokens", "NEAR": round(bought, 4)},
                 {"Stage": "Permanently burned tokens", "NEAR": round(burned, 4)},
                 {"Stage": "Issuance minus burns", "NEAR": round(delta, 4)}],
        "supports": "The same volume can have very different token effects depending on revenue retention and allocation.",
        "investment_link": "A long-term thesis needs an explicit economic bridge from adoption to NEAR token demand or supply effects.",
        "limits": "This is a scenario, not empirical evidence, a valuation, a price forecast or a committed buyback policy. "
                  "Purchases held in treasury do not reduce total supply. Other supply events are omitted.",
        "break_even_annual_volume_usd": threshold,
        "chart": [{"label": f"{factor}× volume", "value": round(p["annual_issuance_near"] - burned * factor, 4)}
                  for factor in (0.5, 1, 2, 5)],
    }
