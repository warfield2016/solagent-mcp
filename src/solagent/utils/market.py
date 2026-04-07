"""Market data utilities -- DexScreener API."""

import re

import httpx

DEXSCREENER_URL = "https://api.dexscreener.com"
_BASE58_RE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


def _is_valid_mint(s: str) -> bool:
    return bool(_BASE58_RE.match(s))


def _safe_float(val, default: float = 0.0) -> float:
    try:
        return float(val) if val is not None and val != "" else default
    except (ValueError, TypeError):
        return default


async def get_token_price(mint_address: str) -> dict | None:
    """Get current token price from DexScreener."""
    if not _is_valid_mint(mint_address):
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DEXSCREENER_URL}/tokens/v1/solana/{mint_address}",
            )
            if resp.status_code != 200:
                return None
            pairs = resp.json()
            if not isinstance(pairs, list) or not pairs:
                return None
            top_pair = pairs[0]
            return {
                "price": top_pair.get("priceUsd", "0"),
                "name": top_pair.get("baseToken", {}).get("name", ""),
                "symbol": top_pair.get("baseToken", {}).get("symbol", ""),
                "volume_24h": _safe_float(top_pair.get("volume", {}).get("h24")),
                "price_change_24h": _safe_float(top_pair.get("priceChange", {}).get("h24")),
                "liquidity_usd": _safe_float(top_pair.get("liquidity", {}).get("usd")),
            }
    except httpx.HTTPError:
        return None


async def search_token_dexscreener(query: str) -> list[dict]:
    """Search for tokens on DexScreener."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DEXSCREENER_URL}/latest/dex/search",
                params={"q": query},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
            pairs = data.get("pairs", []) if isinstance(data, dict) else []
            solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]
            results = []
            for pair in solana_pairs[:10]:
                base = pair.get("baseToken", {})
                results.append({
                    "name": base.get("name", "Unknown"),
                    "symbol": base.get("symbol", "???"),
                    "address": base.get("address", ""),
                    "price_usd": pair.get("priceUsd", "0"),
                    "volume_24h": _safe_float(pair.get("volume", {}).get("h24")),
                    "price_change_24h": _safe_float(pair.get("priceChange", {}).get("h24")),
                    "liquidity_usd": _safe_float(pair.get("liquidity", {}).get("usd")),
                    "pair_address": pair.get("pairAddress", ""),
                })
            return results
    except httpx.HTTPError:
        return []


async def get_trending_tokens() -> list[dict]:
    """Get trending Solana tokens by paid boosts on DexScreener."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{DEXSCREENER_URL}/token-boosts/top/v1",
            )
            if resp.status_code != 200:
                return []
            tokens = resp.json()
            if not isinstance(tokens, list):
                return []
            solana_tokens = [
                t for t in tokens if t.get("chainId") == "solana"
            ][:15]
            return [
                {
                    "description": t.get("description", ""),
                    "url": t.get("url", ""),
                    "token_address": t.get("tokenAddress", ""),
                    "boost_amount": t.get("amount", 0),
                    "total_boost": t.get("totalAmount", 0),
                }
                for t in solana_tokens
            ]
    except httpx.HTTPError:
        return []
