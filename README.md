# solagent-mcp

Solana MCP server for AI agents. Query wallets, swap tokens, send SOL, check prices — all through the Model Context Protocol.

## Tools

| Tool | Description |
|------|-------------|
| `solana_get_balance` | SOL balance + USD value |
| `solana_get_token_balances` | All SPL token holdings |
| `solana_get_transactions` | Recent transaction history |
| `solana_swap_quote` | Jupiter swap quote with routing |
| `solana_execute_swap` | Build unsigned swap transaction |
| `solana_send_sol` | Build unsigned SOL transfer |
| `solana_get_price` | Live token price (DexScreener) |
| `solana_search_token` | Search tokens by name/symbol |
| `solana_trending_tokens` | Top trending Solana tokens |

## Install

```bash
pip install solagent-mcp
```

Or from source:

```bash
git clone https://github.com/anthropic-solagent/solagent-mcp
cd solagent-mcp
pip install -e .
```

## Usage with Claude Code

Add to your MCP config:

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

Or run directly:

```bash
solagent
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `HELIUS_API_KEY` | Helius RPC API key ([get one free](https://dev.helius.xyz/)) | Public RPC |
| `SOLANA_RPC_URL` | Custom Solana RPC endpoint | Auto (Helius or public) |

## Supported tokens

SOL, USDC, USDT, BONK, JUP, RAY, ORCA — or pass any mint address directly.

## Architecture

```
solagent/
├── server.py           # MCP server (FastMCP)
├── tools/
│   ├── wallet.py       # Balance, tokens, history
│   ├── swap.py         # Jupiter swap quote + build
│   ├── transfer.py     # SOL transfers
│   └── market_tools.py # Prices, trending, search
└── utils/
    ├── solana_client.py # Solana JSON-RPC
    ├── jupiter.py       # Jupiter aggregator API
    └── market.py        # DexScreener API
```

## License

MIT
