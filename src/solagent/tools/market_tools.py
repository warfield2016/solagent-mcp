"""Market data -- prices, trending, search."""

from solagent.utils.jupiter import resolve_mint, KNOWN_TOKENS
from solagent.utils.market import (
    get_token_price as _get_price,
    search_token_dexscreener,
    get_trending_tokens as _get_trending,
)


async def get_token_price(token: str) -> dict:
    """Get current USD price of a Solana token."""
    try:
        mint = resolve_mint(token)
        price_data = await _get_price(mint)

        if not price_data:
            return {"token": token, "mint": mint, "error": "Price not found."}

        return {
            "token": token,
            "mint": mint,
            "price_usd": price_data.get("price", "0"),
            "name": price_data.get("name", ""),
            "symbol": price_data.get("symbol", ""),
            "volume_24h": price_data.get("volume_24h", 0),
            "price_change_24h": price_data.get("price_change_24h", 0),
        }
    except Exception as exc:
        return {"token": token, "error": f"Price lookup failed: {type(exc).__name__}"}


async def search_token(query: str) -> dict:
    """Search Solana tokens by name, symbol, or address."""
    try:
        upper = query.upper()
        if upper in KNOWN_TOKENS:
            price_data = await _get_price(KNOWN_TOKENS[upper])
            return {
                "query": query,
                "results": [{
                    "name": upper,
                    "symbol": upper,
                    "address": KNOWN_TOKENS[upper],
                    "price_usd": price_data.get("price", "0") if price_data else "unknown",
                }],
            }

        results = await search_token_dexscreener(query)
        return {"query": query, "result_count": len(results), "results": results}
    except Exception as exc:
        return {"query": query, "error": f"Search failed: {type(exc).__name__}"}


async def get_trending_tokens() -> dict:
    """Get top boosted Solana tokens on DexScreener."""
    try:
        trending = await _get_trending()
        return {"count": len(trending), "trending_tokens": trending}
    except Exception as exc:
        return {"error": f"Trending lookup failed: {type(exc).__name__}"}
