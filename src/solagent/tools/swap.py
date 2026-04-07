"""Token swap via Jupiter aggregator."""

from solagent.utils.jupiter import (
    get_swap_quote as _get_quote,
    get_swap_transaction,
    resolve_mint,
)

TOKEN_DECIMALS = {
    "SOL": 9,
    "USDC": 6,
    "USDT": 6,
    "BONK": 5,
    "JUP": 6,
    "RAY": 6,
    "ORCA": 6,
}


def _get_decimals(token: str) -> int:
    upper = token.upper()
    if upper in TOKEN_DECIMALS:
        return TOKEN_DECIMALS[upper]
    if len(token) >= 32:
        return 9  # assume native decimals for raw mint addresses
    raise ValueError(
        f"Unknown token '{token}'. Use a mint address or add it to TOKEN_DECIMALS."
    )


async def get_swap_quote(
    input_token: str,
    output_token: str,
    amount: float,
    slippage_bps: int = 50,
) -> dict:
    """Get a Jupiter swap quote for a Solana token pair."""
    slippage_bps = max(1, min(slippage_bps, 500))

    in_decimals = _get_decimals(input_token)
    amount_raw = int(amount * (10 ** in_decimals))

    input_mint = resolve_mint(input_token)
    output_mint = resolve_mint(output_token)
    quote = await _get_quote(input_mint, output_mint, amount_raw, slippage_bps)

    out_decimals = _get_decimals(output_token)
    out_amount_raw = int(quote.get("outAmount", 0))
    out_amount = out_amount_raw / (10 ** out_decimals)

    return {
        "input_token": input_token,
        "output_token": output_token,
        "input_amount": amount,
        "output_amount": round(out_amount, 6),
        "price_impact_pct": quote.get("priceImpactPct", "0"),
        "slippage_bps": slippage_bps,
        "route_plan_steps": len(quote.get("routePlan", [])),
        "_raw_quote": quote,
    }


async def execute_swap(
    input_token: str,
    output_token: str,
    amount: float,
    wallet_public_key: str,
    slippage_bps: int = 50,
) -> dict:
    """Build an unsigned swap transaction via Jupiter."""
    quote_result = await get_swap_quote(input_token, output_token, amount, slippage_bps)
    raw_quote = quote_result.pop("_raw_quote")

    swap_tx = await get_swap_transaction(raw_quote, wallet_public_key)

    return {
        **quote_result,
        "status": "transaction_ready",
        "swap_transaction": swap_tx.get("swapTransaction", ""),
        "message": (
            f"Swap transaction built: {amount} {input_token} -> "
            f"~{quote_result['output_amount']} {output_token}. "
            "Sign and broadcast to execute."
        ),
    }
