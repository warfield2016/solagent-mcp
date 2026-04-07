"""Wallet tools — balance, tokens, transactions."""

from solders.pubkey import Pubkey

from solagent.utils.solana_client import solana
from solagent.utils.jupiter import resolve_mint
from solagent.utils.market import get_token_price


def _validate_address(address: str) -> str | None:
    try:
        Pubkey.from_string(address)
        return None
    except Exception:
        return f"Invalid Solana address: {address}"


async def get_sol_balance(address: str) -> dict:
    """Get SOL balance and USD estimate for a wallet."""
    if err := _validate_address(address):
        return {"error": err}

    balance = await solana.get_balance(address)
    sol_price_info = await get_token_price(resolve_mint("SOL"))
    usd_price = float(sol_price_info.get("price", 0)) if sol_price_info else 0

    return {
        "address": address,
        "balance_sol": round(balance, 6),
        "balance_usd": round(balance * usd_price, 2),
        "sol_price_usd": round(usd_price, 2),
    }


async def get_token_balances(address: str) -> dict:
    """Get all SPL token balances for a wallet."""
    if err := _validate_address(address):
        return {"error": err}

    tokens = await solana.get_token_accounts(address)
    return {
        "address": address,
        "token_count": len(tokens),
        "tokens": tokens,
    }


async def get_transaction_history(address: str, limit: int = 10) -> dict:
    """Get recent transactions for a wallet."""
    if err := _validate_address(address):
        return {"error": err}

    limit = max(1, min(limit, 20))
    txs = await solana.get_recent_transactions(address, limit=limit)
    return {
        "address": address,
        "transaction_count": len(txs),
        "transactions": txs,
    }
