"""Inspect the API's supported-asset catalog, not a quote or execution benchmark."""
from collections import Counter
from .common import TOKENS_URL, fetch_json, metric, now


def collect():
    return {"catalog": {"endpoint": TOKENS_URL, "observed_at": now(), "response": fetch_json(TOKENS_URL)}}


def analyze(evidence):
    tokens = evidence["catalog"]["response"]
    if not isinstance(tokens, list) or not tokens:
        raise ValueError("Expected a non-empty token catalog")
    seen = set()
    chains = Counter()
    symbols = set()
    for token in tokens:
        asset_id, chain, symbol = token["assetId"], token["blockchain"], token["symbol"]
        if not all(isinstance(v, str) and v for v in (asset_id, chain, symbol)):
            raise ValueError("Unexpected asset metadata")
        if asset_id in seen:
            raise ValueError("Duplicate asset IDs: catalog counts need review")
        seen.add(asset_id)
        chains[chain] += 1
        symbols.add(symbol)
    return {
        "headline": "One API surface across multiple chain catalogs.",
        "summary": f"The current response lists {len(seen)} distinct asset IDs across {len(chains)} "
                   "blockchain labels. Counts are calculated directly from the saved API response.",
        "metrics": [metric("Asset IDs", len(seen)), metric("Chain labels", len(chains)),
                    metric("Symbol labels", len(symbols))],
        "rows": [{"Chain": chain, "Catalog assets": count} for chain, count in sorted(chains.items())],
        "supports": "A single documented integration surface enumerates assets from multiple chains.",
        "investment_link": "Broader integration reach can expose NEAR-based infrastructure to activity beyond its native chain.",
        "limits": "Catalog inclusion does not prove every route has liquidity, competitive pricing, successful settlement "
                  "or active users. Symbol labels can represent different assets; prices are not analyzed here.",
    }
