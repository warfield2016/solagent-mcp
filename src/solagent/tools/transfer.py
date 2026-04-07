"""SOL transfer via Solana RPC."""

from solders.pubkey import Pubkey

from solagent.utils.solana_client import LAMPORTS_PER_SOL

MAX_TRANSFER_SOL = 1000


async def send_sol(to_address: str, amount_sol: float) -> dict:
    """Build an unsigned SOL transfer transaction."""
    try:
        Pubkey.from_string(to_address)
    except Exception:
        return {"error": f"Invalid recipient address: {to_address}"}

    if amount_sol <= 0:
        return {"error": "Amount must be positive."}

    if amount_sol > MAX_TRANSFER_SOL:
        return {"error": f"Amount exceeds safety cap of {MAX_TRANSFER_SOL} SOL."}

    lamports = int(round(amount_sol * LAMPORTS_PER_SOL))

    return {
        "status": "unsigned",
        "to": to_address,
        "amount_sol": amount_sol,
        "amount_lamports": lamports,
        "message": f"Transfer {amount_sol} SOL to {to_address}. Sign externally to broadcast.",
    }
