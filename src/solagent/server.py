"""FastMCP server exposing Solana RPC, Jupiter swap, and market data tools."""

import json
from mcp.server.fastmcp import FastMCP

from solagent.tools.wallet import get_sol_balance, get_token_balances, get_transaction_history
from solagent.tools.swap import get_swap_quote, execute_swap
from solagent.tools.transfer import send_sol, send_token
from solagent.tools.market_tools import get_token_price, search_token, get_trending_tokens
from solagent.utils.solana_client import solana

mcp = FastMCP(
    "SolAgent",
    instructions="Solana MCP server. Query balances, swap tokens via Jupiter, send SOL/tokens, check prices, find trending tokens, and inspect accounts.",
)


# ── Wallet ──────────────────────────────────────────────────

@mcp.tool()
async def solana_get_balance(address: str) -> str:
    """Get SOL balance and USD value for a Solana wallet."""
    return json.dumps(await get_sol_balance(address), indent=2)


@mcp.tool()
async def solana_get_token_balances(address: str) -> str:
    """Get all SPL token balances for a Solana wallet."""
    return json.dumps(await get_token_balances(address), indent=2)


@mcp.tool()
async def solana_get_transactions(address: str, limit: int = 10) -> str:
    """Get recent transactions for a Solana wallet (max 20)."""
    return json.dumps(await get_transaction_history(address, limit), indent=2)


# ── Swap (Jupiter) ─────────────────────────────────────────

@mcp.tool()
async def solana_swap_quote(
    input_token: str, output_token: str, amount: float, slippage_bps: int = 50
) -> str:
    """Get a Jupiter swap quote. Accepts token symbols (SOL, USDC, JUP, BONK) or mint addresses."""
    result = await get_swap_quote(input_token, output_token, amount, slippage_bps)
    result.pop("_raw_quote", None)
    return json.dumps(result, indent=2)


@mcp.tool()
async def solana_execute_swap(
    input_token: str, output_token: str, amount: float,
    wallet_public_key: str, slippage_bps: int = 50,
) -> str:
    """Build an unsigned swap transaction via Jupiter. Returns metadata for external signing."""
    result = await execute_swap(input_token, output_token, amount, wallet_public_key, slippage_bps)
    has_tx = bool(result.pop("swap_transaction", ""))
    result["has_transaction"] = has_tx
    return json.dumps(result, indent=2)


# ── Transfer ────────────────────────────────────────────────

@mcp.tool()
async def solana_send_sol(to_address: str, amount_sol: float) -> str:
    """Build an unsigned SOL transfer. Returns transaction details for external signing."""
    return json.dumps(await send_sol(to_address, amount_sol), indent=2)


@mcp.tool()
async def solana_send_token(to_address: str, token: str, amount: float) -> str:
    """Build an unsigned SPL token transfer. Accepts symbol (USDC, BONK) or mint address."""
    return json.dumps(await send_token(to_address, token, amount), indent=2)


# ── Market Data ─────────────────────────────────────────────

@mcp.tool()
async def solana_get_price(token: str) -> str:
    """Get current USD price of a Solana token. Accepts symbol or mint address."""
    return json.dumps(await get_token_price(token), indent=2)


@mcp.tool()
async def solana_search_token(query: str) -> str:
    """Search Solana tokens by name, symbol, or address."""
    return json.dumps(await search_token(query), indent=2)


@mcp.tool()
async def solana_trending_tokens() -> str:
    """Get top trending Solana tokens right now."""
    return json.dumps(await get_trending_tokens(), indent=2)


# ── Account Info ────────────────────────────────────────────

@mcp.tool()
async def solana_account_info(address: str) -> str:
    """Get account info for any Solana address: balance, owner program, executable flag."""
    try:
        from solagent.tools.wallet import _validate_address
        if err := _validate_address(address):
            return json.dumps({"error": err})
        result = await solana.get_account_info(address)
        return json.dumps(result, indent=2)
    except Exception as exc:
        return json.dumps({"error": f"Account lookup failed: {type(exc).__name__}"})


# ── Resources ───────────────────────────────────────────────

@mcp.resource("solana://wallet/{address}")
async def wallet_resource(address: str) -> str:
    """Wallet overview for a Solana address."""
    balance = await get_sol_balance(address)
    tokens = await get_token_balances(address)
    return json.dumps({"balance": balance, "tokens": tokens}, indent=2)


# ── Entry Point ─────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
