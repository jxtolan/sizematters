/**
 * Authentication utilities for Solana wallet signature verification
 * Supports session tokens for better UX (sign once, use for 1 hour)
 */

import { WalletContextState } from '@solana/wallet-adapter-react';
import bs58 from 'bs58';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const SESSION_TOKEN_KEY = 'smart_money_session_token';
const SESSION_WALLET_KEY = 'smart_money_session_wallet';

export interface SignedRequest {
  walletAddress: string;
  signature: string;
  message: string;
}

export interface SessionToken {
  token: string;
  wallet_address: string;
  expires_at: string;
}

/**
 * Generate a timestamp-based message for signing
 * This prevents replay attacks by including a timestamp
 * Note: No newlines allowed (HTTP header restrictions)
 */
export function generateAuthMessage(): string {
  const timestamp = Date.now();
  const message = `Smart Money Tinder Authentication | Timestamp: ${timestamp}`;
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
 * Get stored session token from localStorage
 */
export function getStoredSessionToken(): SessionToken | null {
  if (typeof window === 'undefined') return null;
  
  const token = localStorage.getItem(SESSION_TOKEN_KEY);
  const wallet = localStorage.getItem(SESSION_WALLET_KEY);
  const expires = localStorage.getItem(`${SESSION_TOKEN_KEY}_expires`);
  
  if (!token || !wallet || !expires) return null;
  
  // Check if expired
  if (new Date(expires) < new Date()) {
    clearSessionToken();
    return null;
  }
  
  return {
    token,
    wallet_address: wallet,
    expires_at: expires
  };
}

/**
 * Store session token in localStorage
 */
export function storeSessionToken(sessionData: SessionToken): void {
  if (typeof window === 'undefined') return;
  
  localStorage.setItem(SESSION_TOKEN_KEY, sessionData.token);
  localStorage.setItem(SESSION_WALLET_KEY, sessionData.wallet_address);
  localStorage.setItem(`${SESSION_TOKEN_KEY}_expires`, sessionData.expires_at);
}

/**
 * Clear session token from localStorage
 */
export function clearSessionToken(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(SESSION_TOKEN_KEY);
  localStorage.removeItem(SESSION_WALLET_KEY);
  localStorage.removeItem(`${SESSION_TOKEN_KEY}_expires`);
}

/**
 * Get or create a session token
 * Signs once, stores token, reuses for 1 hour
 */
export async function getOrCreateSession(wallet: WalletContextState): Promise<string> {
  if (!wallet.connected || !wallet.publicKey) {
    throw new Error('Wallet not connected');
  }
  
  const currentWallet = wallet.publicKey.toBase58();
  
  // Check for existing valid session
  const stored = getStoredSessionToken();
  if (stored && stored.wallet_address === currentWallet) {
    return stored.token;
  }
  
  // Need to create new session - sign message
  console.log('🎫 Creating new session (signing required)...');
  const { walletAddress, signature, message } = await signAuthMessage(wallet);
  
  // Request session token from backend
  const response = await axios.post(`${API_BASE}/api/auth/session`, {
    wallet_address: walletAddress,
    signature,
    message
  });
  
  const sessionData: SessionToken = {
    token: response.data.session_token,
    wallet_address: response.data.wallet_address,
    expires_at: response.data.expires_at
  };
  
  storeSessionToken(sessionData);
  console.log('✅ Session created! Valid for 1 hour.');
  
  return sessionData.token;
}

/**
 * Create authenticated request headers
 * Uses session token if available (NO SIGNING!), otherwise signs to get token
 * 
 * @param wallet - The connected Solana wallet
 * @returns Promise with headers object containing authentication data
 */
export async function getAuthHeaders(
  wallet: WalletContextState
): Promise<Record<string, string>> {
  try {
    // Try to get or create session token
    const token = await getOrCreateSession(wallet);
    
    return {
      'Content-Type': 'application/json',
      'X-Session-Token': token,
    };
  } catch (error) {
    // If session creation fails, fall back to just wallet address (for development mode)
    console.warn('Session creation failed, falling back to basic auth:', error);
    
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

