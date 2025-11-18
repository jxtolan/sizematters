"""
Authentication middleware for Solana wallet signature verification
"""

from fastapi import Header, HTTPException
from typing import Optional
import base58
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def verify_wallet_signature(
    wallet_address: str,
    signature: str,
    message: str
) -> bool:
    """
    Verify that a signature was created by the wallet owner
    
    Args:
        wallet_address: Solana wallet public key (base58)
        signature: Signature bytes (base58 encoded)
        message: Original message that was signed
        
    Returns:
        bool: True if signature is valid
    """
    try:
        # Decode the public key
        public_key_bytes = base58.b58decode(wallet_address)
        verify_key = VerifyKey(public_key_bytes)
        
        # Decode the signature
        signature_bytes = base58.b58decode(signature)
        
        # Verify the signature
        verify_key.verify(message.encode('utf-8'), signature_bytes)
        return True
    except (BadSignatureError, Exception) as e:
        print(f"❌ Signature verification failed: {e}")
        return False


async def get_authenticated_wallet(
    x_wallet_address: Optional[str] = Header(None),
    x_wallet_signature: Optional[str] = Header(None),
    x_message: Optional[str] = Header(None)
) -> str:
    """
    Dependency to verify wallet ownership via signature
    
    Usage in endpoints:
        @app.post("/api/protected")
        async def protected_endpoint(wallet: str = Depends(get_authenticated_wallet)):
            # wallet is now verified!
    """
    if not x_wallet_address or not x_wallet_signature or not x_message:
        raise HTTPException(
            status_code=401,
            detail="Missing authentication headers: X-Wallet-Address, X-Wallet-Signature, X-Message"
        )
    
    # Verify the signature
    if not verify_wallet_signature(x_wallet_address, x_wallet_signature, x_message):
        raise HTTPException(
            status_code=401,
            detail="Invalid wallet signature"
        )
    
    return x_wallet_address


async def verify_wallet_match(
    wallet_address: str,
    authenticated_wallet: str
) -> None:
    """
    Verify that the authenticated wallet matches the requested wallet
    
    Usage:
        await verify_wallet_match(wallet_address, authenticated_wallet)
    """
    if wallet_address != authenticated_wallet:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own resources"
        )

