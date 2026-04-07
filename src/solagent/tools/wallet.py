"""Wallet tools -- balance, tokens, transactions."""

from solders.pubkey import Pubkey

from solagent.utils.solana_client import solana
from solagent.utils.jupiter import resolve_mint
from solagent.utils.market import get_token_price, _safe_float


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

    try:
        balance = await solana.get_balance(address)
        sol_price_info = await get_token_price(resolve_mint("SOL"))
        usd_price = _safe_float(sol_price_info.get("price")) if sol_price_info else 0.0

        return {
            "address": address,
            "balance_sol": round(balance, 6),
            "balance_usd": round(balance * usd_price, 2),
            "sol_price_usd": round(usd_price, 2),
        }
    except Exception as exc:
        return {"error": f"Failed to fetch balance: {type(exc).__name__}"}


async def get_token_balances(address: str) -> dict:
    """Get all SPL token balances for a wallet."""
    if err := _validate_address(address):
        return {"error": err}

    try:
        tokens = await solana.get_token_accounts(address)
        return {
            "address": address,
            "token_count": len(tokens),
            "tokens": tokens,
        }
    except Exception as exc:
        return {"error": f"Failed to fetch token balances: {type(exc).__name__}"}


async def get_transaction_history(address: str, limit: int = 10) -> dict:
    """Get recent transactions for a wallet."""
    if err := _validate_address(address):
        return {"error": err}

    try:
        limit = max(1, min(limit, 20))
        txs = await solana.get_recent_transactions(address, limit=limit)
        return {
            "address": address,
            "transaction_count": len(txs),
            "transactions": txs,
        }
    except Exception as exc:
        return {"error": f"Failed to fetch transactions: {type(exc).__name__}"}
