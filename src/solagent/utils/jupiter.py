"""Jupiter Swap API client."""

import httpx

JUPITER_API_URL = "https://api.jup.ag"
JUPITER_QUOTE_URL = f"{JUPITER_API_URL}/swap/v1/quote"
JUPITER_SWAP_URL = f"{JUPITER_API_URL}/swap/v1/swap"

KNOWN_TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
}


def resolve_mint(token: str) -> str:
    """Resolve token symbol to mint address. Passes through raw addresses."""
    upper = token.upper()
    return KNOWN_TOKENS.get(upper, token)


async def get_swap_quote(
    input_mint: str,
    output_mint: str,
    amount_raw: int,
    slippage_bps: int = 50,
) -> dict:
    """Fetch a swap quote from Jupiter."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            JUPITER_QUOTE_URL,
            params={
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount_raw),
                "slippageBps": slippage_bps,
            },
        )
        resp.raise_for_status()
        return resp.json()


async def get_swap_transaction(
    quote_response: dict,
    user_public_key: str,
) -> dict:
    """Build a swap transaction from a Jupiter quote."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            JUPITER_SWAP_URL,
            json={
                "quoteResponse": quote_response,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True,
                "prioritizationFeeLamports": "auto",
            },
        )
        resp.raise_for_status()
        return resp.json()
