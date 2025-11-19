/**
 * Authentication utilities for Solana wallet signature verification
 */

import { WalletContextState } from '@solana/wallet-adapter-react';
import bs58 from 'bs58';

export interface SignedRequest {
  walletAddress: string;
  signature: string;
  message: string;
}

/**
 * Generate a timestamp-based message for signing
 * This prevents replay attacks by including a timestamp
 */
export function generateAuthMessage(): string {
  const timestamp = Date.now();
  const message = `Smart Money Tinder Authentication\nTimestamp: ${timestamp}`;
  return message;
}

/**
 * Sign a message with the connected wallet
 * 
 * @param wallet - The connected Solana wallet
 * @param message - The message to sign (optional, will generate if not provided)
 * @returns Promise with wallet address, signature, and message
 * @throws Error if wallet is not connected or signature fails
 */
export async function signAuthMessage(
  wallet: WalletContextState,
  message?: string
): Promise<SignedRequest> {
  // Check if wallet is connected
  if (!wallet.connected || !wallet.publicKey) {
    throw new Error('Wallet not connected');
  }

  // Check if wallet supports message signing
  if (!wallet.signMessage) {
    throw new Error('Wallet does not support message signing');
  }

  // Generate message if not provided
  const authMessage = message || generateAuthMessage();

  try {
    // Sign the message
    const messageBytes = new TextEncoder().encode(authMessage);
    const signatureBytes = await wallet.signMessage(messageBytes);

    // Convert signature to base58
    const signature = bs58.encode(signatureBytes);

    // Get wallet address
    const walletAddress = wallet.publicKey.toBase58();

    return {
      walletAddress,
      signature,
      message: authMessage,
    };
  } catch (error) {
    console.error('Failed to sign message:', error);
    throw new Error('Failed to sign authentication message');
  }
}

/**
 * Create authenticated request headers
 * 
 * @param wallet - The connected Solana wallet
 * @returns Promise with headers object containing authentication data
 */
export async function getAuthHeaders(
  wallet: WalletContextState
): Promise<Record<string, string>> {
  try {
    const { walletAddress, signature, message } = await signAuthMessage(wallet);

    return {
      'Content-Type': 'application/json',
      'X-Wallet-Address': walletAddress,
      'X-Wallet-Signature': signature,
      'X-Signature-Message': message,
    };
  } catch (error) {
    // If signing fails, fall back to just wallet address (for development mode)
    console.warn('Signature generation failed, falling back to basic auth:', error);
    
    if (wallet.connected && wallet.publicKey) {
      return {
        'Content-Type': 'application/json',
        'X-Wallet-Address': wallet.publicKey.toBase58(),
      };
    }

    throw error;
  }
}

/**
 * Check if signature verification is likely enabled on the backend
 * This is a helper to provide better UX
 */
export function isSignatureRequired(): boolean {
  // You can add logic here to check backend config if needed
  // For now, we'll always try to provide signatures when possible
  return true;
}

