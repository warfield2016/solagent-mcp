"""SOL and SPL token transfers."""

from solders.pubkey import Pubkey

from solagent.utils.solana_client import solana, LAMPORTS_PER_SOL
from solagent.utils.jupiter import resolve_mint, KNOWN_TOKENS
from solagent.tools.swap import TOKEN_DECIMALS

MAX_TRANSFER_SOL = 1000

# SPL Associated Token Account program
ATA_PROGRAM = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"


def _validate_pubkey(address: str, label: str = "address") -> str | None:
    try:
        Pubkey.from_string(address)
        return None
    except Exception:
        return f"Invalid {label}: {address}"


async def send_sol(to_address: str, amount_sol: float) -> dict:
    """Build an unsigned SOL transfer."""
    if err := _validate_pubkey(to_address, "recipient address"):
        return {"error": err}

    if amount_sol <= 0:
        return {"error": "Amount must be positive."}

    if amount_sol > MAX_TRANSFER_SOL:
        return {"error": f"Amount exceeds safety cap of {MAX_TRANSFER_SOL} SOL."}

    lamports = int(round(amount_sol * LAMPORTS_PER_SOL))

    return {
        "status": "unsigned",
        "type": "sol_transfer",
        "to": to_address,
        "amount_sol": amount_sol,
        "amount_lamports": lamports,
        "message": f"Transfer {amount_sol} SOL to {to_address}. Sign externally to broadcast.",
    }


async def send_token(
    to_address: str,
    token: str,
    amount: float,
) -> dict:
    """Build an unsigned SPL token transfer."""
    if err := _validate_pubkey(to_address, "recipient address"):
        return {"error": err}

    if amount <= 0:
        return {"error": "Amount must be positive."}

    mint = resolve_mint(token)
    if err := _validate_pubkey(mint, "token mint"):
        return {"error": err}

    # Resolve decimals
    upper = token.upper()
    if upper in TOKEN_DECIMALS:
        decimals = TOKEN_DECIMALS[upper]
    else:
        # For raw mint addresses, try to fetch decimals from chain
        try:
            token_info = await solana.get_mint_info(mint)
            decimals = token_info.get("decimals", 9)
        except Exception:
            decimals = 9  # fallback

    raw_amount = int(round(amount * (10 ** decimals)))

    return {
        "status": "unsigned",
        "type": "spl_transfer",
        "to": to_address,
        "token": token,
        "mint": mint,
        "amount": amount,
        "raw_amount": raw_amount,
        "decimals": decimals,
        "ata_program": ATA_PROGRAM,
        "message": (
            f"Transfer {amount} {token} (mint: {mint[:12]}...) to {to_address}. "
            "Ensure recipient has an Associated Token Account for this mint. "
            "Sign externally to broadcast."
        ),
    }
