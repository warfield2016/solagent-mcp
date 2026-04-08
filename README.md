# SolAgent

Solana MCP server for AI agents. Query wallets, swap tokens via Jupiter, send SOL/tokens, and track markets — all through Claude or any MCP-compatible client.

## Install

```bash
git clone https://github.com/warfield2016/solagent-mcp.git
cd solagent-mcp
pip install -e .
```

## Configure

```bash
cp .env.example .env
# Edit .env — add your Helius API key (free at https://dev.helius.xyz/)
```

## Use with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "solagent": {
      "command": "solagent",
      "env": {
        "HELIUS_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `solana_get_balance` | SOL balance + USD value |
| `solana_get_token_balances` | All SPL token balances (Token + Token-2022) |
| `solana_get_transactions` | Recent transaction history |
| `solana_swap_quote` | Jupiter swap quote with routing |
| `solana_execute_swap` | Build unsigned swap TX |
| `solana_send_sol` | Build unsigned SOL transfer |
| `solana_send_token` | Build unsigned SPL token transfer |
| `solana_get_price` | Token price (DexScreener) |
| `solana_search_token` | Search by name/symbol/address |
| `solana_trending_tokens` | Trending tokens on Solana |
| `solana_account_info` | Account details: owner, executable, balance |

## Architecture

```
server.py          FastMCP entry point + 11 tool definitions
tools/
  wallet.py        Balance, tokens, transactions
  transfer.py      SOL + SPL token transfers (unsigned)
  swap.py          Jupiter swap quotes + TX building
  market_tools.py  Prices, search, trending
utils/
  solana_client.py JSON-RPC client (Token + Token-2022, account info)
  jupiter.py       Jupiter Swap API client
  market.py        DexScreener API client
```

## Security

- No private keys stored, passed, or logged
- All write tools return unsigned transactions for external signing
- SSRF protection: base58 validation on all mint addresses
- Slippage capped at 1% (100 bps)
- Transfer cap: 1000 SOL per transaction
- RPC errors sanitized — no API keys or server details leak

## License

MIT
