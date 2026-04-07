"""SOL transfer via Solana RPC."""

import base64

from solders.hash import Hash
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer, TransferParams
from solders.transaction import Transaction
from solders.message import Message

from solagent.utils.solana_client import solana, LAMPORTS_PER_SOL


async def send_sol(to_address: str, amount_sol: float) -> dict:
    """Build an unsigned SOL transfer transaction."""
    lamports = int(amount_sol * LAMPORTS_PER_SOL)

    try:
        recipient = Pubkey.from_string(to_address)
    except Exception:
        return {"error": f"Invalid recipient address: {to_address}"}

    if amount_sol <= 0:
        return {"error": "Amount must be positive"}

    return {
        "status": "unsigned",
        "to": to_address,
        "amount_sol": amount_sol,
        "amount_lamports": lamports,
        "message": f"Transfer {amount_sol} SOL to {to_address}. Sign externally to broadcast.",
    }
