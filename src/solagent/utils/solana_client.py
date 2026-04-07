"""Solana JSON-RPC client."""

import os

import httpx

HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")
SOLANA_RPC_URL = os.environ.get(
    "SOLANA_RPC_URL",
    f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}"
    if HELIUS_API_KEY
    else "https://api.mainnet-beta.solana.com",
)

LAMPORTS_PER_SOL = 1_000_000_000


class SolanaClient:
    def __init__(self, rpc_url: str = SOLANA_RPC_URL):
        self.rpc_url = rpc_url
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def rpc_call(self, method: str, params: list | None = None) -> dict:
        client = await self._get_client()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or [],
        }
        resp = await client.post(self.rpc_url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise Exception(f"RPC error: {data['error']}")
        return data.get("result", {})

    async def get_balance(self, address: str) -> float:
        result = await self.rpc_call("getBalance", [address])
        return result.get("value", 0) / LAMPORTS_PER_SOL

    async def get_token_accounts(self, address: str) -> list[dict]:
        result = await self.rpc_call(
            "getTokenAccountsByOwner",
            [
                address,
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"},
            ],
        )
        accounts = []
        for item in result.get("value", []):
            try:
                info = item["account"]["data"]["parsed"]["info"]
                token_amount = info.get("tokenAmount", {})
                ui_amount = float(token_amount.get("uiAmount") or 0)
                if ui_amount > 0:
                    accounts.append({
                        "mint": info["mint"],
                        "amount": token_amount.get("uiAmountString", "0"),
                        "decimals": token_amount.get("decimals", 0),
                    })
            except (KeyError, TypeError, ValueError):
                continue
        return accounts

    async def get_recent_transactions(self, address: str, limit: int = 10) -> list[dict]:
        limit = max(1, min(limit, 100))
        signatures = await self.rpc_call(
            "getSignaturesForAddress",
            [address, {"limit": limit}],
        )
        return [
            {
                "signature": s["signature"],
                "slot": s.get("slot"),
                "block_time": s.get("blockTime"),
                "err": s.get("err"),
                "memo": s.get("memo"),
            }
            for s in signatures
        ]

    async def get_latest_blockhash(self) -> str:
        result = await self.rpc_call(
            "getLatestBlockhash", [{"commitment": "finalized"}]
        )
        return result["value"]["blockhash"]

    async def send_raw_transaction(self, raw_tx: str) -> str:
        return await self.rpc_call(
            "sendTransaction",
            [raw_tx, {"encoding": "base64", "skipPreflight": False}],
        )

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


solana = SolanaClient()
