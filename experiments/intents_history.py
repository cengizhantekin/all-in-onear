"""Compare published NEAR Intents activity and fee series on matched UTC days."""
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from .common import INTENTS_HISTORY_URLS, fetch_json, metric, now

PERIODS = (
    (date(2026, 9, 13), date(2026, 10, 12)),
    (date(2026, 10, 13), date(2026, 11, 11)),
)


def collect():
    observations = {}
    for name, url in INTENTS_HISTORY_URLS.items():
        response = fetch_json(url)
        observations[name] = {"endpoint": url, "observed_at": now(), "response": response}
    return observations


def series(name, observation):
    if observation["endpoint"] != INTENTS_HISTORY_URLS[name]:
        raise ValueError(f"Unexpected source for {name}")
    captured = datetime.fromisoformat(observation["observed_at"])
    if captured.utcoffset() is None or captured.astimezone(timezone.utc).date() <= PERIODS[-1][1]:
        raise ValueError(f"{name} was captured before the comparison window ended")
    response = observation["response"]
    if response["slug"] != "near-intents" or response["module"] != "near-intents":
        raise ValueError(f"{name} does not identify NEAR Intents")
    points = {}
    for stamp, value in response["totalDataChart"]:
        if type(stamp) is not int or stamp % 86400 != 0:
            raise ValueError(f"{name} uses a timestamp outside UTC day boundaries")
        day = datetime.fromtimestamp(stamp, timezone.utc).date()
        if day in points:
            raise ValueError(f"Duplicate {name} observation on {day}")
        if type(value) not in (int, float):
            raise ValueError(f"Invalid {name} value on {day}")
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError(f"Invalid {name} value on {day}")
        points[day] = amount
    return points


def total(points, name, first, last):
    days = [first + timedelta(days=i) for i in range((last - first).days + 1)]
    missing = [day.isoformat() for day in days if day not in points]
    if missing:
        raise ValueError(f"{name} is missing UTC days: {', '.join(missing[:5])}")
    return sum(points[day] for day in days)


def monthly_volume(points, cutoff):
    first_day = min(points)
    month = first_day.replace(day=1)
    if first_day != month:
        month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    months = []
    while month < cutoff.replace(day=1):
        next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        days = [month + timedelta(days=i) for i in range((next_month - month).days)]
        months.append({
            "month": month.strftime("%Y-%m"),
            "volume_usd": float(sum(points[day] for day in days)) if all(day in points for day in days) else None,
        })
        month = next_month
    return months


def analyze(evidence):
    if set(evidence) != set(INTENTS_HISTORY_URLS):
        raise ValueError("Expected the volume, gross fee and wallet revenue captures")
    points = {name: series(name, record) for name, record in evidence.items()}
    rows = []
    for first, last in PERIODS:
        volume = total(points["volume"], "volume", first, last)
        fees = total(points["fees"], "fees", first, last)
        revenue = total(points["revenue"], "revenue", first, last)
        if volume <= 0:
            raise ValueError("Cannot calculate ratios without positive swap volume")
        rows.append({
            "Period (inclusive UTC)": f"{first.isoformat()} to {last.isoformat()}",
            "Days in all three series": (last - first).days + 1,
            "Swap volume (USD)": float(volume),
            "Gross swap fees (USD)": float(fees),
            "Reported wallet revenue (USD)": float(revenue),
            "Gross fees / volume (bps)": float(round(fees * 10000 / volume, 4)),
            "Wallet revenue / volume (bps)": float(round(revenue * 10000 / volume, 4)),
        })
    latest = rows[-1]
    return {
        "headline": "Compare Intents volume, fees and reported wallet revenue.",
        "summary": f"In the latest 30-day window, the source reports ${latest['Swap volume (USD)']:,.0f} of swap volume, "
                   f"${latest['Gross swap fees (USD)']:,.0f} in gross swap fees and "
                   f"${latest['Reported wallet revenue (USD)']:,.0f} in wallet revenue. "
                   "All three series cover the same 60 UTC dates across both windows.",
        "metrics": [metric("Latest swap volume", latest["Swap volume (USD)"], "USD"),
                    metric("Latest gross swap fees", latest["Gross swap fees (USD)"], "USD"),
                    metric("Latest reported wallet revenue", latest["Reported wallet revenue (USD)"], "USD"),
                    metric("Wallet revenue / volume", latest["Wallet revenue / volume (bps)"], "bps")],
        "rows": rows,
        "monthly_swap_volume": monthly_volume(points["volume"], PERIODS[-1][1]),
        "supports": "The published series connect Intents usage to measured fees and flows into designated revenue wallets "
                    "over the same calendar windows. The wallet measure uses the adapter's NEAR/wNEAR transfer filters.",
        "investment_link": "Tracking activity and wallet revenue over the same periods helps test whether recurring usage contributes economic value.",
        "limits": "DefiLlama aggregates upstream data and can revise past dates. "
                  "Wallet transfers can be swept after the associated swaps, so the revenue ratio compares period totals. "
                  "Gross fees include affiliate fees. The wallet revenue measure does not establish executed buybacks, burns, "
                  "profit, or the relationship between any individual swap and any individual wallet transfer.",
        "latest_period": latest["Period (inclusive UTC)"],
        "days_compared": 60,
    }
