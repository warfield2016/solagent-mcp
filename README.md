# SolAgent

Solana MCP server for AI agents. Query wallets, swap tokens via Jupiter, send SOL, and track markets — all through Claude or any MCP-compatible client.

## Install

```bash
git clone https://github.com/anthropics/solagent.git  # update URL
cd solagent
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
| `solana_get_token_balances` | All SPL token balances |
| `solana_get_transactions` | Recent transaction history |
| `solana_swap_quote` | Jupiter swap quote |
| `solana_execute_swap` | Build unsigned swap TX |
| `solana_send_sol` | Build unsigned SOL transfer |
| `solana_get_price` | Token price (DexScreener) |
| `solana_search_token` | Search by name/symbol |
| `solana_trending_tokens` | Trending tokens on Solana |

## Architecture

```
server.py          FastMCP entry point + tool definitions
tools/
  wallet.py        Balance, tokens, transactions
  transfer.py      SOL transfers (unsigned)
  swap.py          Jupiter swap quotes + TX building
  market_tools.py  Prices, search, trending
utils/
  solana_client.py JSON-RPC client
  jupiter.py       Jupiter API client
  market.py        DexScreener API client
```

## License

MIT
