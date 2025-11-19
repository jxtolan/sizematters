"""
Test signature verification
"""
import base58
from nacl.signing import VerifyKey, SigningKey
from nacl.exceptions import BadSignatureError

def test_signature():
    print("=" * 60)
    print("🧪 Testing Signature Verification")
    print("=" * 60)
    print()
    
    # Generate a test keypair
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    
    # Get the public key (wallet address equivalent)
    public_key_bytes = bytes(verify_key)
    wallet_address = base58.b58encode(public_key_bytes).decode('ascii')
    
    print(f"✅ Generated test wallet: {wallet_address[:20]}...")
    print()
    
    # Create a message
    message = "Smart Money Tinder Authentication\nTimestamp: 1234567890"
    message_bytes = message.encode('utf-8')
    
    # Sign the message
    signature_bytes = signing_key.sign(message_bytes).signature
    signature = base58.b58encode(signature_bytes).decode('ascii')
    
    print(f"✅ Signed message")
    print(f"   Message: {message[:50]}...")
    print(f"   Signature: {signature[:30]}...")
    print()
    
    # Now verify it (like the backend does)
    try:
        # Decode public key
        pk_bytes = base58.b58decode(wallet_address)
        vk = VerifyKey(pk_bytes)
        
        # Decode signature
        sig_bytes = base58.b58decode(signature)
        
        # Verify
        vk.verify(message_bytes, sig_bytes)
        
        print("✅ Signature verification SUCCEEDED!")
        print()
        print("=" * 60)
        print("🎉 Signature system is working correctly!")
        print("=" * 60)
        return True
        
    except BadSignatureError as e:
        print(f"❌ Signature verification FAILED: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_signature()

