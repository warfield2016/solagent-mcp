"""Market data utilities — prices, trending tokens, search."""

import httpx

DEXSCREENER_URL = "https://api.dexscreener.com"


async def get_token_price(mint_address: str) -> dict | None:
    """Get current token price from DexScreener (free, no auth)."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{DEXSCREENER_URL}/tokens/v1/solana/{mint_address}",
        )
        if resp.status_code != 200:
            return None
        pairs = resp.json()
        if not pairs:
            return None
        top_pair = pairs[0] if isinstance(pairs, list) else pairs
        return {
            "price": top_pair.get("priceUsd", "0"),
            "name": top_pair.get("baseToken", {}).get("name", ""),
            "symbol": top_pair.get("baseToken", {}).get("symbol", ""),
            "volume_24h": top_pair.get("volume", {}).get("h24", 0),
            "price_change_24h": top_pair.get("priceChange", {}).get("h24", 0),
            "liquidity_usd": top_pair.get("liquidity", {}).get("usd", 0),
        }


async def search_token_dexscreener(query: str) -> list[dict]:
    """Search for tokens on DexScreener."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{DEXSCREENER_URL}/latest/dex/search",
            params={"q": query},
        )
        if resp.status_code != 200:
            return []
        pairs = resp.json().get("pairs", [])
        solana_pairs = [p for p in pairs if p.get("chainId") == "solana"]
        results = []
        for pair in solana_pairs[:10]:
            base = pair.get("baseToken", {})
            results.append({
                "name": base.get("name", "Unknown"),
                "symbol": base.get("symbol", "???"),
                "address": base.get("address", ""),
                "price_usd": pair.get("priceUsd", "0"),
                "volume_24h": pair.get("volume", {}).get("h24", 0),
                "price_change_24h": pair.get("priceChange", {}).get("h24", 0),
                "liquidity_usd": pair.get("liquidity", {}).get("usd", 0),
                "pair_address": pair.get("pairAddress", ""),
            })
        return results


async def get_trending_tokens() -> list[dict]:
    """Get trending Solana tokens from DexScreener."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://api.dexscreener.com/token-boosts/top/v1",
        )
        if resp.status_code != 200:
            return []
        tokens = resp.json()
        solana_tokens = [
            t for t in tokens if t.get("chainId") == "solana"
        ][:15]
        results = []
        for t in solana_tokens:
            results.append({
                "name": t.get("description", "Unknown"),
                "url": t.get("url", ""),
                "token_address": t.get("tokenAddress", ""),
                "amount": t.get("amount", 0),
                "total_amount": t.get("totalAmount", 0),
            })
        return results
