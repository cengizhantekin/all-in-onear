"""Observe a finalized block and read its pinned protocol configuration."""
from .common import metric, rpc


def collect():
    block = rpc("block", {"finality": "final"})
    header = block["response"]["result"]["header"]
    config = rpc("EXPERIMENTAL_protocol_config", {"block_id": header["hash"]})
    return {"block": block, "config": config}


def analyze(evidence):
    block = evidence["block"]["response"]["result"]
    config = evidence["config"]["response"]["result"]
    header = block["header"]
    if config.get("chain_id") != "mainnet":
        raise ValueError("Expected NEAR mainnet configuration")
    if evidence["config"]["request"]["params"].get("block_id") != header["hash"]:
        raise ValueError("Configuration must be pinned to the observed block")
    chunks = block.get("chunks", [])
    shard_ids = sorted({chunk["shard_id"] for chunk in chunks})
    included = sum(chunk.get("height_included") == header["height"] for chunk in chunks)
    return {
        "headline": "One finalized block, multiple shard records.",
        "summary": f"Block {header['height']:,} contains records for {len(shard_ids)} shards. "
                   "The protocol configuration was requested at this exact block hash.",
        "metrics": [metric("Block height", header["height"]), metric("Shard records", len(shard_ids)),
                    metric("New chunks in block", included), metric("Protocol version", config["protocol_version"])],
        "rows": [{"Shard": c["shard_id"], "Included at height": c["height_included"],
                  "New in this block": c["height_included"] == header["height"]} for c in chunks],
        "supports": "NEAR exposes a sharded execution structure through a public, reproducible read-only query.",
        "investment_link": "Parallel execution is a technical foundation for serving more applications and agent workloads.",
        "limits": "This is a single-block capability observation. It does not measure TPS, dynamic resharding, "
                  "transaction completion latency, decentralization or economic demand.",
        "block_height": header["height"], "block_hash": header["hash"],
    }
